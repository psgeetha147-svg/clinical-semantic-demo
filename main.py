import pandas as pd

df = pd.read_csv("diabetic_data.csv")

print(df.head())
print("Number of records:", len(df))
print("Number of columns:", len(df.columns))

patients = df.head(100)

print(patients)
print("Selected patients:", len(patients))
patients.to_csv("100_patients.csv", index=False)