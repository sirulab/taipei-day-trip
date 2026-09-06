from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
import mysql.connector
from database import get_db_connection
from models import *
from fastapi.staticfiles import StaticFiles
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Header

app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

SECRET_KEY = 'safer_secret_key_for_taipei_trip'
ALGORITHM = 'HS256'
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
    return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
    return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
    return FileResponse("./static/thankyou.html", media_type="text/html")

###
def get_images(cursor, attraction_ids: list):
    if not attraction_ids:
        return {}
    format_strings = ','.join(['%s'] * len(attraction_ids))
    sql = f"SELECT attraction_id, url FROM image WHERE attraction_id IN ({format_strings})"
    cursor.execute(sql, tuple(attraction_ids))
    images_map = {att_id: [] for att_id in attraction_ids}
    for att_id, url in cursor.fetchall():
        images_map[att_id].append(url)
    return images_map


@app.get("/api/attractions", 
    tags=["Attraction"],
    summary="取得景點資料列表")
def get_attractions(
    page: int = Query(...),
    category: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None)):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) # dictionary=True >attraction_ids.append(row["id"]) /n TypeError: tuple indices must be integers or slices, not str

        limit = 8
        offset = page * limit

        conditions = []
        params = []

        if category:
            conditions.append("category = %s")
            params.append(category)
            
        if keyword:
            conditions.append("(mrt = %s OR name LIKE %s)")
            params.append(keyword)
            params.append(f"%{keyword}%")

        # 多撈一筆法（ LIMIT 9 ）# 查詢總資料筆數（ COUNT(*) ）		
        if len(conditions) > 0:
            where_clause = " WHERE " + " AND ".join(conditions)
        else:
            where_clause = ""

        sql = f"""
            SELECT id, name, category, description, address, 
            transport, mrt, lat, lng
            FROM attraction
            {where_clause}
            LIMIT %s OFFSET %s
        """
        cursor.execute(sql, tuple(params + [limit + 1, offset]))
        rows = cursor.fetchall()

        if len(rows) > limit:
            next_page = page + 1
        else:
            next_page = None
        data = rows[:limit]  # 只需要前 8 筆資料

        attraction_ids = []
        for row in data:
            attraction_ids.append(row["id"])

        if attraction_ids:
            img_cursor = conn.cursor()
            images_map = get_images(img_cursor, attraction_ids)
            img_cursor.close()
            
            for item in data:
                item["images"] = images_map.get(item["id"], [])

        return {"nextPage": next_page, "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.get("/api/attraction/{attractionId}",
    tags=["Attraction"],
    summary="根據景點編號取得景點資料")
def get_attraction_by_id(attractionId: int = Path(...)):
    conn = None # 例如：資料庫密碼寫錯、MySQL 沒開、連線池滿了/ finally 在清理與關閉連線時，不會「找不到變數名稱」崩潰
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        sql = """
            SELECT id, name, category, description, address, 
            transport, mrt, lat, lng
            FROM attraction
            WHERE id = %s
        """
        cursor.execute(sql, (attractionId,))
        row = cursor.fetchone()
        
        if not row:
            return JSONResponse(status_code=400, content={"error": True, "message": "景點編號不正確"})
        
        img_cursor = conn.cursor()
        images_map = get_images(img_cursor, [attractionId])
        img_cursor.close()
        
        row["images"] = images_map.get(attractionId, [])
        
        return {"data": row}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.get("/api/categories",
    tags=["Attraction Category"],
    summary="取得景點分類名稱列表")
def get_categories():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = "SELECT DISTINCT category FROM attraction WHERE category IS NOT NULL AND category != ''"
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        categories = [row[0] for row in rows]
        return {"data": categories}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.get("/api/mrts",
    tags=["MRT Station"],
    summary="取得捷運站名稱列表")
def get_mrts():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """
            SELECT mrt FROM attraction 
            WHERE mrt IS NOT NULL AND mrt != '' 
            GROUP BY mrt 
            ORDER BY COUNT(id) DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        mrts = [row[0] for row in rows]
        return {"data": mrts}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            
def verify_token(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None

@app.post("/api/sign_up",
    tags=["User"],
    summary="註冊一個新的會員")
def sign_up(user: UserSignUp):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        hashed_password = bcrypt_context.hash(user.password)
        sql_insert = "INSERT INTO user (name, email, hashed_password) VALUES (%s, %s, %s)"
        cursor.execute(sql_insert, (user.name, user.email, hashed_password))
        conn.commit()
        
        return {"ok": True}
        
    except mysql.connector.errors.IntegrityError:
        if conn: conn.rollback()
        return JSONResponse(status_code=400, content={"error": True, "message": "此電子郵件已被註冊"})
    except Exception as e:
        if conn: conn.rollback()
        print(e)
        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.post("/api/sign_in",
    tags=["User"],
    summary="登入會員帳戶")
def sign_in(user: UserSignIn):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        sql = "SELECT id, name, email, hashed_password FROM user WHERE email = %s"
        cursor.execute(sql, (user.email,))
        db_user = cursor.fetchone()
        
        if not db_user or not bcrypt_context.verify(user.password, db_user["hashed_password"]):
            return JSONResponse(status_code=400, content={"error": True, "message": "帳號或密碼不正確"})
        
        payload = {
            "id": db_user["id"],
            "name": db_user["name"],
            "email": db_user["email"],
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        return {"token": token}
        
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.get("/api/auth",
    tags=['User'],
    summary="取得當前登入的會員資訊")
def get_current_user(authorization: Optional[str] = Header(None)):
    user_payload = verify_token(authorization)
    
    if not user_payload:
        return {"data": None}
    
    return {
        "data": {
            "id": user_payload["id"],
            "name": user_payload["name"],
            "email": user_payload["email"]
        }
    }
@app.post("/api/booking",
    tags=["Booking"],
    summary="建立新的預定行程")
def create_booking(booking: BookingRequest, authorization: Optional[str] = Header(None)):
    user_payload = verify_token(authorization)
    if not user_payload:
        return JSONResponse(status_code=403, content={"error": True, "message": "未登入系統，拒絕存取"})
    
    user_email = user_payload["email"]

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("DELETE FROM booking WHERE email = %s", (user_email,))
        
        sql_insert = """
        INSERT INTO booking
        (attractionId, date, time, price, email) 
        VALUES 
        (%s, %s, %s, %s, %s)
        """
        val = (booking.attractionId, booking.date, booking.time, booking.price, user_email) 

        cursor.execute(sql_insert, val)
        conn.commit()
        
        return {"ok": True}
        
    except Exception as e:
        if conn: conn.rollback()
        print(e)
        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.get("/api/booking",
    tags=["Booking"],
    summary="取得尚未確認下單的預定行程")
def read_booking(authorization: Optional[str] = Header(None), ):
    # token 取得 user_email
    # user_email 一次對應一個 attractionid (修改booking以email為key) 新的override舊的
    # user_email(user_id) 一次對應多個attractionid
    user_payload = verify_token(authorization)
    if not user_payload:
        return JSONResponse(status_code=403, content={"error": True, "message": "未登入系統，拒絕存取"})
    
    user_email = user_payload["email"]
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT 
                b.date, b.time, b.price,
                a.id AS attraction_id, a.name, a.address,
                (SELECT url FROM image WHERE attraction_id = a.id LIMIT 1) AS image_url
            FROM booking b
            JOIN attraction a ON b.attractionId = a.id
            WHERE b.email = %s
        """
        cursor.execute(sql, (user_email,))
        row = cursor.fetchone()

        if not row:
            return {"data": None}

        return {
            "data": {
                "attraction": {
                    "id": row["attraction_id"],
                    "name": row["name"],
                    "address": row["address"],
                    "image": row["image_url"]
                },
                "date": row["date"], # 格式
                "time": row["time"],
                "price": row["price"]
            }
        }
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"}) # status code
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()        

@app.delete("/api/booking",
    tags=["Booking"],
    summary="刪除目前的預定行程")
def delete_booking(authorization: Optional[str] = Header(None)):
    user_payload = verify_token(authorization)
    if not user_payload:
        return JSONResponse(status_code=403, content={"error": True, "message": "未登入系統，拒絕存取"})
    
    user_email = user_payload["email"]
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = "DELETE FROM booking WHERE email = %s"
        cursor.execute(sql, (user_email,))
        conn.commit()

        return {"ok": True}
        
    except Exception as e:
        if conn: conn.rollback()
        print(f"DELETE Booking Error: {e}")
        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()