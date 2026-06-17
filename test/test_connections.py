import psycopg2
import cohere
from dotenv import load_dotenv
import os


#testing the .env loader
load_dotenv()

print("Testing Connection...\n")

#testing database connection
print("Testing connections with database...\n")

try:
    conn = psycopg2.connect(
        host = os.getenv("DB_HOST"),
        port = os.getenv("DB_PORT"),
        dbname = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD")

    )
    print("Database connected successfully..")
    conn.close()
except Exception as e:
    print("Failed...\n",e)

#testing cohere connection

print("Testing connections with cohere...\n")

try:
    co = cohere.ClientV2(os.getenv("COHERE_API_KEY"))
    response = co.chat(
        model="command-r-plus-08-2024",
        messages = [{"role": "user", "content": "Greet the user in one word"}]
    )
    print("Cohere is successfully connected...")
    print("Response:", response.message.content[0].text)

except Exception as e:
    print("Connection FAILED...\n", e)