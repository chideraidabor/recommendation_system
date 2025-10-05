import pandas as pd
from collections import defaultdict, Counter
from datetime import timedelta

# Load invoice data
df = pd.read_csv("../Data/invoices.csv")
df['date'] = pd.to_datetime(df['date'])

# Compatibility dictionary (embedded directly)
compatibility = {
    'DO101': ['HI101', 'KN101', 'HA101', 'PA101', 'NA101', 'LO101'],
    'DO102': ['HI102', 'KN102', 'HA102', 'PA102', 'NA102', 'LO102'],
    'DO103': ['HI103', 'KN103', 'HA103', 'PA103', 'NA103', 'LO103'],
    'DO104': ['HI104', 'KN104', 'HA104', 'PA104', 'NA104', 'LO104'],
    'DO105': ['HI105', 'KN105', 'HA105', 'PA105', 'NA105', 'LO105'],
    'DO106': ['HI106', 'KN106', 'HA106', 'PA106', 'NA106', 'LO106'],
    'DO107': ['HI107', 'KN107', 'HA107', 'PA107', 'NA107', 'LO107'],
    'DO108': ['HI108', 'KN108', 'HA108', 'PA108', 'NA108', 'LO108'],
    'DO109': ['HI109', 'KN109', 'HA109', 'PA109', 'NA109', 'LO109'],
    'DO110': ['HI110', 'KN110', 'HA110', 'PA110', 'NA110', 'LO110'],
    'WI101': ['FR101', 'SE101', 'HA101', 'LO101', 'SC101', 'TR101'],
    'WI102': ['FR102', 'SE102', 'HA102', 'LO102', 'SC102', 'TR102'],
    'WI103': ['FR103', 'SE103', 'HA103', 'LO103', 'SC103', 'TR103'],
    'WI104': ['FR104', 'SE104', 'HA104', 'LO104', 'SC104', 'TR104'],
    'WI105': ['FR105', 'SE105', 'HA105', 'LO105', 'SC105', 'TR105'],
    'WI106': ['FR106', 'SE106', 'HA106', 'LO106', 'SC106', 'TR106'],
    'WI107': ['FR107', 'SE107', 'HA107', 'LO107', 'SC107', 'TR107'],
    'WI108': ['FR108', 'SE108', 'HA108', 'LO108', 'SC108', 'TR108'],
    'WI109': ['FR109', 'SE109', 'HA109', 'LO109', 'SC109', 'TR109'],
    'WI110': ['FR110', 'SE110', 'HA110', 'LO110', 'SC110', 'TR110'],
    'SI101': ['FA101', 'DR101', 'PI101', 'MO101', 'SE101', 'CA101'],
    'SI102': ['FA102', 'DR102', 'PI102', 'MO102', 'SE102', 'CA102'],
    'SI103': ['FA103', 'DR103', 'PI103', 'MO103', 'SE103', 'CA103'],
    'SI104': ['FA104', 'DR104', 'PI104', 'MO104', 'SE104', 'CA104'],
    'SI105': ['FA105', 'DR105', 'PI105', 'MO105', 'SE105', 'CA105'],
    'SI106': ['FA106', 'DR106', 'PI106', 'MO106', 'SE106', 'CA106'],
    'SI107': ['FA107', 'DR107', 'PI107', 'MO107', 'SE107', 'CA107'],
    'SI108': ['FA108', 'DR108', 'PI108', 'MO108', 'SE108', 'CA108'],
    'SI109': ['FA109', 'DR109', 'PI109', 'MO109', 'SE109', 'CA109'],
    'SI110': ['FA110', 'DR110', 'PI110', 'MO110', 'SE110', 'CA110'],
    'SH101': ['FA101', 'HE101', 'HO101', 'CU101', 'VA101', 'TR101'],
    'SH102': ['FA102', 'HE102', 'HO102', 'CU102', 'VA102', 'TR102'],
    'SH103': ['FA103', 'HE103', 'HO103', 'CU103', 'VA103', 'TR103'],
    'SH104': ['FA104', 'HE104', 'HO104', 'CU104', 'VA104', 'TR104'],
    'SH105': ['FA105', 'HE105', 'HO105', 'CU105', 'VA105', 'TR105'],
    'SH106': ['FA106', 'HE106', 'HO106', 'CU106', 'VA106', 'TR106'],
    'SH107': ['FA107', 'HE107', 'HO107', 'CU107', 'VA107', 'TR107'],
    'SH108': ['FA108', 'HE108', 'HO108', 'CU108', 'VA108', 'TR108'],
    'SH109': ['FA109', 'HE109', 'HO109', 'CU109', 'VA109', 'TR109'],
    'SH110': ['FA110', 'HE110', 'HO110', 'CU110', 'VA110', 'TR110'],
    'MI101': ['FR101', 'MO101', 'LI101', 'SC101', 'AD101', 'TR101'],
    'MI102': ['FR102', 'MO102', 'LI102', 'SC102', 'AD102', 'TR102'],
    'MI103': ['FR103', 'MO103', 'LI103', 'SC103', 'AD103', 'TR103'],
    'MI104': ['FR104', 'MO104', 'LI104', 'SC104', 'AD104', 'TR104'],
    'MI105': ['FR105', 'MO105', 'LI105', 'SC105', 'AD105', 'TR105'],
    'MI106': ['FR106', 'MO106', 'LI106', 'SC106', 'AD106', 'TR106'],
    'MI107': ['FR107', 'MO107', 'LI107', 'SC107', 'AD107', 'TR107'],
    'MI108': ['FR108', 'MO108', 'LI108', 'SC108', 'AD108', 'TR108'],
    'MI109': ['FR109', 'MO109', 'LI109', 'SC109', 'AD109', 'TR109'],
    'MI110': ['FR110', 'MO110', 'LI110', 'SC110', 'AD110', 'TR110'],
    'CA101': ['HA101', 'HI101', 'SH101', 'PA101', 'LO101', 'KN101'],
    'CA102': ['HA102', 'HI102', 'SH102', 'PA102', 'LO102', 'KN102'],
    'CA103': ['HA103', 'HI103', 'SH103', 'PA103', 'LO103', 'KN103'],
    'CA104': ['HA104', 'HI104', 'SH104', 'PA104', 'LO104', 'KN104'],
    'CA105': ['HA105', 'HI105', 'SH105', 'PA105', 'LO105', 'KN105'],
    'CA106': ['HA106', 'HI106', 'SH106', 'PA106', 'LO106', 'KN106'],
    'CA107': ['HA107', 'HI107', 'SH107', 'PA107', 'LO107', 'KN107'],
    'CA108': ['HA108', 'HI108', 'SH108', 'PA108', 'LO108', 'KN108'],
    'CA109': ['HA109', 'HI109', 'SH109', 'PA109', 'LO109', 'KN109'],
    'CA110': ['HA110', 'HI110', 'SH110', 'PA110', 'LO110', 'KN110'],
}

# Build reverse compatibility dictionary
reverse_compatibility = defaultdict(list)
for main_item, compatible_items in compatibility.items():
    for comp in compatible_items:
        reverse_compatibility[comp].append(main_item)

# Initialize co-occurrence matrix
co_occurrence = defaultdict(Counter)

# Group by customer
grouped = df.groupby('customer_id')

# Loop through each customer's transactions
for customer_id, group in grouped:
    group = group.sort_values('date')

    for i in range(len(group)):
        item_i = group.iloc[i]['part_number']
        date_i = group.iloc[i]['date']

        # Filter items within ±30 days
        window = group[(group['date'] >= date_i - timedelta(days=30)) &
                       (group['date'] <= date_i + timedelta(days=30))]

        for item_j in window['part_number'].unique():
            if item_i == item_j:
                continue

            # Check compatibility in both directions
            if item_j in compatibility.get(item_i, []):
                co_occurrence[item_i][item_j] += 1
            if item_i in compatibility.get(item_j, []):
                co_occurrence[item_j][item_i] += 1

            # Check reverse compatibility
            if item_j in reverse_compatibility.get(item_i, []):
                co_occurrence[item_i][item_j] += 1
            if item_i in reverse_compatibility.get(item_j, []):
                co_occurrence[item_j][item_i] += 1

# Convert to DataFrame and print
co_occurrence_df = pd.DataFrame(co_occurrence).fillna(0).astype(int)
print(co_occurrence_df)