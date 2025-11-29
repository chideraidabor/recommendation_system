import pandas as pd
from itertools import combinations
import numpy as np
import sqlite3

print("\n=== LOADING CLEAN DATA ===")

df = pd.read_csv("../Data/generated_invoices_updated.csv")

# 🔥 Remove duplicate rows
df = df.drop_duplicates()

# ============================
# COMPATIBILITY DEFINITIONS
# ============================

compatibility_rules = {
    "DOOR": ["HINGE", "KNOB", "LOCK"],
    "WINDOW": ["FRAME", "SCREEN", "HANDLE"],
    "SINK": ["FAUCET", "DRAIN", "CABINET"]
}

# EXPAND COMPATIBILITY (SINK CLUSTER)
# Cabinet should also be compatible with Faucet and Drain
compatibility_rules["CABINET"] = ["SINK", "FAUCET", "DRAIN"]
compatibility_rules["FAUCET"] = ["SINK", "CABINET", "DRAIN"]
compatibility_rules["DRAIN"]  = ["SINK", "CABINET", "FAUCET"]
compatibility_rules["CABINET"] = ["SINK", "FAUCET", "DRAIN"]

# Expand DOOR cluster
compatibility_rules["DOOR"] = ["HINGE", "KNOB", "LOCK"]
compatibility_rules["HINGE"] = ["DOOR", "KNOB", "LOCK"]
compatibility_rules["KNOB"]  = ["DOOR", "HINGE", "LOCK"]
compatibility_rules["LOCK"]  = ["DOOR", "HINGE", "KNOB"]

# Expand WINDOW cluster
compatibility_rules["WINDOW"] = ["FRAME", "SCREEN", "HANDLE"]
compatibility_rules["FRAME"]  = ["WINDOW", "SCREEN", "HANDLE"]
compatibility_rules["SCREEN"] = ["WINDOW", "FRAME", "HANDLE"]
compatibility_rules["HANDLE"] = ["WINDOW", "FRAME", "SCREEN"]

prefix_map = {
    "DO": "DOOR",
    "HI": "HINGE",
    "KN": "KNOB",
    "LO": "LOCK",

    "WI": "WINDOW",
    "FR": "FRAME",
    "SC": "SCREEN",
    "HA": "HANDLE",

    "SI": "SINK",
    "FA": "FAUCET",
    "DR": "DRAIN",
    "CA": "CABINET",
}

def is_compatible(item1, item2):
    t1 = prefix_map.get(item1[:2])
    t2 = prefix_map.get(item2[:2])
    if not t1 or not t2:
        return False
    return (t2 in compatibility_rules.get(t1, [])) or (t1 in compatibility_rules.get(t2, []))


# ============================
# CO-OCCURRENCE MATRIX
# ============================

items = sorted(df["part_number"].unique())
co_matrix = pd.DataFrame(0, index=items, columns=items)

for invoice_id, group in df.groupby("invoice_id"):

    # Use UNIQUE part numbers to avoid inflated pairs
    items_in_invoice = group["part_number"].unique().tolist()

    if len(items_in_invoice) < 2:
        continue

    for a, b in combinations(items_in_invoice, 2):
        co_matrix.loc[a, b] += 1
        co_matrix.loc[b, a] += 1

co_matrix.to_csv("co_occurrence_matrix_raw_fixed.csv")


# ============================
# APPLY COMPATIBILITY FILTER
# ============================

filtered_matrix = co_matrix.copy()

for i in items:
    for j in items:
        if i != j and filtered_matrix.loc[i, j] > 0:
            if not is_compatible(i, j):
                filtered_matrix.loc[i, j] = 0

filtered_matrix.to_csv("co_occurrence_matrix_filtered_fixed.csv")


# ============================
# COSINE SIMILARITY
# ============================

def cosine_similarity_matrix(co_mat):
    similarity = pd.DataFrame(0.0, index=co_mat.index, columns=co_mat.columns)
    supports = (co_mat > 0).sum(axis=1)

    for i in co_mat.index:
        for j in co_mat.columns:
            if i == j:
                similarity.loc[i, j] = 1.0
            else:
                cij = co_mat.loc[i, j]
                if cij > 0:
                    denom = np.sqrt(supports[i] * supports[j])
                    similarity.loc[i, j] = cij / denom if denom > 0 else 0.0

    return similarity


cosine_sim_matrix = cosine_similarity_matrix(filtered_matrix)
cosine_sim_matrix.to_csv("cosine_similarity_matrix_fixed.csv")


# ============================
# TOP-N RECOMMENDER
# ============================

def get_top_recommendations(item_id, top_n=5):
    sims = cosine_sim_matrix.loc[item_id].drop(item_id)
    sims = sims[sims > 0]

    if sims.empty:
        print(f"[WARNING] No compatible co-occurrences found for {item_id}")
        return pd.DataFrame(columns=["recommended_item", "score"])

    sims = sims.sort_values(ascending=False)

    return pd.DataFrame({
        "recommended_item": sims.head(top_n).index,
        "score": sims.head(top_n).values
    })


def build_top_n_table(top_n=5):
    records = []
    for item_id in cosine_sim_matrix.index:
        top_recs = get_top_recommendations(item_id, top_n=top_n)
        for _, row in top_recs.iterrows():
            records.append({
                "item_id": item_id,
                "recommended_item": row["recommended_item"],
                "cosine_similarity": row["score"]
            })
    return pd.DataFrame(records)


# ============================
# STORE IN SQLITE
# ============================

def store_recommendations_in_db(top_n_table, db_path="../Database/recommendation.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Recommendations")
    top_n_table.to_sql("Recommendations", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()
    print(f"Stored {len(top_n_table)} recommendations")


# ============================
# RUN
# ============================

print("\n=== BUILDING TOP-N TABLE ===")
top_n_table = build_top_n_table(top_n=5)
top_n_table.to_csv("top_n_recommendations_clean.csv", index=False)

store_recommendations_in_db(top_n_table)

print("\nTEST: DR102 recommendations:")
print(get_top_recommendations("DR102"))
