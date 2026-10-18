from pymongo import MongoClient
import pprint

client = MongoClient("mongodb://localhost:27017/")
db = client["medical"]
col = db["medical"]

output_file = open("results.txt", "w", encoding="utf-8")

def log(text=""):
    print(text)
    output_file.write(str(text) + "\n")

log(f"Всього документів: {col.count_documents({})}")

# Крок 1
pipeline1 = [
    {"$count": "total_documents"},
    {"$out": "step1_result"}
]
col.aggregate(pipeline1)
log("\n--- Крок 1 ---")
for doc in db.step1_result.find():
    log(pprint.pformat(doc))

# Крок 2
pipeline2 = [
    {
        "$group": {
            "_id": None,
            "max_covered_charges": {"$max": "$Average_Covered_Charges"}
        }
    },
    {"$out": "step2_result"}
]
col.aggregate(pipeline2)
log("\n--- Крок 2 ---")
for doc in db.step2_result.find():
    log(pprint.pformat(doc))

# Крок 3
pipeline3 = [
    {
        "$group": {
            "_id": "$DRG_Definition",
            "max_covered_charges": {"$max": "$Average_Covered_Charges"}
        }
    },
    {"$sort": {"max_covered_charges": -1}},
    {"$out": "step3_result"}
]
col.aggregate(pipeline3)
log("\n--- Крок 3 ---")
for doc in db.step3_result.find().limit(5):
    log(pprint.pformat(doc))

# Крок 4
pipeline4 = [
    {
        "$group": {
            "_id": "$DRG_Definition",
            "max_covered_charges": {"$max": "$Average_Covered_Charges"}
        }
    },
    {"$match": {"max_covered_charges": {"$gt": 100000}}},
    {"$sort": {"max_covered_charges": -1}},
    {"$out": "step4_result"}
]
col.aggregate(pipeline4)
log("\n--- Крок 4 ---")
for doc in db.step4_result.find().limit(5):
    log(pprint.pformat(doc))

# Крок 5
pipeline5 = [
    {"$match": {"Average_Covered_Charges": {"$lt": 150000}}},
    {
        "$group": {
            "_id": "$DRG_Definition",
            "max_covered_charges": {"$max": "$Average_Covered_Charges"}
        }
    },
    {"$match": {"max_covered_charges": {"$gt": 50000}}},
    {"$sort": {"max_covered_charges": -1}},
    {"$out": "step5_result"}
]
col.aggregate(pipeline5)
log("\n--- Крок 5 ---")
for doc in db.step5_result.find().limit(5):
    log(pprint.pformat(doc))

output_file.close()

