from fastapi import *
from fastapi.responses import FileResponse
from typing import Optional
import mysql.connector
from database import get_db_connection
from models import *

app=FastAPI()

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

@app.get("/api/attractions")
def get_attractions(
    page: int = Query(...),
    category: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None)):

    conn = get_db_connection()
    cursor = conn.cursor() # dictionary=True

    limit = 8
    offset = page * limit

    conditions = []
    params = []

    if category:
        conditions.append("cat = %s")
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
                transport, mrt, latitude AS lat, longitude AS lng
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