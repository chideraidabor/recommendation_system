import pandas as pd
from itertools import combinations
import numpy as np
import sqlite3

# load the invoice data
df = pd.read_csv("../Data/generated_invoices.csv")

# compatibility rule dictionary
compatibility_rules = {
    "DOOR": ["HINGE", "KNOB", "LOCK"],
    "WINDOW": ["FRAME", "SCREEN", "HANDLE"],
    "SINK": ["FAUCET", "DRAIN", "CABINET"]
}

# map compatibility with initials
def is_compatible(item1, item2):
    mapping = {
        "DO": "DOOR", "HI": "HINGE", "KN": "KNOB", "LO": "LOCK",
        "FR": "FRAME", "SC": "SCREEN", "HA": "HANDLE",
        "FA": "FAUCET", "DR": "DRAIN", "CA": "CABINET"
    }
    # check if in our map
    prefix1, prefix2 = item1[:2], item2[:2]
    t1, t2 = mapping.get(prefix1), mapping.get(prefix2)
    if not t1 or not t2:
        return False
    return (t2 in compatibility_rules.get(t1, [])) or (t1 in compatibility_rules.get(t2, []))


# Build the co-occurrence 
items = sorted(df['part_number'].unique())
co_matrix = pd.DataFrame(0, index=items, columns=items)

for invoice_id, group in df.groupby("invoice_id"):
    items_in_invoice = group["part_number"].tolist()
    for a, b in combinations(items_in_invoice, 2):
        co_matrix.loc[a, b] += 1
        co_matrix.loc[b, a] += 1

# initial raw mapping, checking all the occurences
co_matrix.to_csv("co_occurrence_matrix_raw.csv")

# filtering the occurences by compatibility
filtered_matrix = co_matrix.copy()
for i in filtered_matrix.index:
    for j in filtered_matrix.columns:
        if i != j and filtered_matrix.loc[i, j] > 0:
            if not is_compatible(i, j):
                filtered_matrix.loc[i, j] = 0

filtered_matrix.to_csv("co_occurrence_matrix_filtered.csv")


# compute the Cosine Similarity according to Sarwar in paper
def cosine_similarity_matrix(co_mat):
    similarity = pd.DataFrame(0.0, index=co_mat.index, columns=co_mat.columns)
    supports = co_mat.sum(axis=1)  # item supports (# of invoices containing item)

    for i in co_mat.index:
        for j in co_mat.columns:
            if i == j:
                similarity.loc[i, j] = 1.0
            elif co_mat.loc[i, j] > 0:
                denom = np.sqrt(supports[i] * supports[j])
                if denom > 0:
                    similarity.loc[i, j] = co_mat.loc[i, j] / denom

    return similarity

cosine_sim_matrix = cosine_similarity_matrix(filtered_matrix)
cosine_sim_matrix.to_csv("cosine_similarity_matrix.csv")


# recommend top item
def get_top_recommendations(item_id, top_n=5, candidate_pool=10):
    sims = cosine_sim_matrix.loc[item_id].drop(item_id).sort_values(ascending=False)
    candidates = sims.head(candidate_pool)

    # Merge into one DataFrame
    combined = pd.DataFrame({
        "Cosine_Similarity": candidates,
    })
    
    # Re-rank by confidence 
    combined = combined.sort_values(by="Cosine_Similarity", ascending=False)
    
    return combined.head(top_n)

# Store Top-N Recommendations for all items 

def build_top_n_table(top_n=5, candidate_pool=10):
    records = []
    for item_id in cosine_sim_matrix.index:
        recs = get_top_recommendations(item_id, top_n=top_n, candidate_pool=candidate_pool)
        for rec_item, row in recs.iterrows():
            records.append({
                "item_id": item_id,
                "recommended_item": rec_item,
                "cosine_similarity": row["Cosine_Similarity"],
            })
    return pd.DataFrame(records)

# ---- Store Top-N Recommendations in Database ----
def store_recommendations_in_db(top_n_table, db_path="../Database/recommendation.db"):
    # Connect to your SQLite database (or create if not exists)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id TEXT,
        recommended_item TEXT,
        cosine_similarity REAL
    )
    """)

    # Clear old data to avoid duplicates 
    cursor.execute("DELETE FROM Recommendations")

    # Insert all recommendations
    top_n_table.to_sql("Recommendations", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()
    print(f"Stored {len(top_n_table)} recommendations in the database.")

# Build and save Top-N table
# top_n_table = build_top_n_table(top_n=5, candidate_pool=10)
# top_n_table.to_csv("top_n_recommendations.csv", index=False)

top_n_table = build_top_n_table(top_n=5, candidate_pool=10)

# Store it in the database instead of CSV
store_recommendations_in_db(top_n_table)

# Test
print("Cosine Similarity - Top 3 recommendations for DO101:")
print(get_top_recommendations("FA102", top_n=5, candidate_pool=10))