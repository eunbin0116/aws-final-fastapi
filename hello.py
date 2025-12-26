from fastapi import FastAPI, UploadFile, File, Form
import pymysql
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import boto3
import uuid

load_dotenv()

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RDS 연결
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

# 서버 시작 시 이벤트
@app.on_event("startup")
async def startup_event():
    print('server running')
    conn = get_db_connection()
    if conn:
        conn.close()

# 루트 엔드포인트
@app.get("/")
async def root():
    print('hello..' + os.getenv('DB_HOST'))
    return {"message":"Hello...fastapi... edited"}

# 헬스 체크
@app.get("/health")
async def health():
    return {"status": "ok"}

# -----------------------------
# 추가: 이미지 업로드 + DB 저장
# -----------------------------
@app.post("/trips")
async def create_trip(
    title: str = Form(...),
    content: str = Form(...),
    file: UploadFile = File(...)
):
    # 1️⃣ S3 업로드
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )
    bucket_name = os.getenv("S3_BUCKET_NAME")
    file_ext = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    s3_client.upload_fileobj(file.file, bucket_name, unique_filename)
    file_url = f"https://{bucket_name}.s3.amazonaws.com/{unique_filename}"

    # 2️⃣ DB 저장
    conn = get_db_connection()
    if not conn:
        return {"error": "DB 연결 실패"}
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO posts (title, content, image_url) VALUES (%s,%s,%s)"
            cursor.execute(sql, (title, content, file_url))
        conn.commit()
    finally:
        conn.close()

    return {"message": "업로드 성공", "image_url": file_url}
