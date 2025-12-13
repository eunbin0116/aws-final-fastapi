from fastapi import FastAPI
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ RDS 연결 성공!")
        return connection
    except Exception as e:
        print(f"❌ RDS 연결 실패: {e}")
        return None

@app.on_event("startup")
async def startup_event():
    print('server running')
    get_db_connection() #db연결
    
@app.get("/")
async def root():

    print('hello..'+ os.getenv('DB_HOST'))
    return {"message":"Hello...fastapi... edited"}