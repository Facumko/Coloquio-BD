from pymongo import MongoClient


client = MongoClient("mongodb+srv://mirchenkofacu:Facu1234@cluster0.fzd5jif.mongodb.net/")

bd = client["DondeQueda"]

print("BD cargada correctamente")


