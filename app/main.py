from fastapi import FastAPI, HTTPException
from app.athena_client import run_athena_query
from app.models import SQLQueryRequest, EchoRequest, QueryParams

app = FastAPI()

# 🧪 Endpoint Echo Test
@app.post("/echo")
async def echo_test(request: EchoRequest):
    return {"echo": request.message}

# 🧑‍💻 Endpoint para "Usuarios con más cuentas scrapeadas y cantidad de filtros activos"
@app.get("/users/most_scraped")
async def get_users_most_scraped(limit: int = 10):
    query = f"""
    SELECT
      sa.userId,
      COUNT(sa.id) AS accounts_scraped,
      COUNT(uf.id) AS active_filters
    FROM scraped_acount sa
    LEFT JOIN user_apify_filters uf ON uf.historial_id IN (
      SELECT id FROM user_apify_call_historial WHERE user_id = sa.userId
    )
    GROUP BY sa.userId
    ORDER BY accounts_scraped DESC
    LIMIT {limit}
    """
    try:
        result = run_athena_query(query)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🧑‍💻 Endpoint para "Admins activos con preguntas respondidas y promedio de vistas"
@app.get("/admins/questions_and_views")
async def get_admins_with_questions_and_views(is_active: str, limit: int = 10):
    query = f"""
    SELECT
      ap.id AS admin_id,
      ap.is_active,
      COUNT(qa.id) AS questions_answered,
      COALESCE(AVG(atm.views), 0) AS avg_views
    FROM admin_profiles ap
    LEFT JOIN quest_and_answer qa ON qa.admin_id = ap.id
    LEFT JOIN admin_tiktok_metrics atm ON atm.adminid = ap.id
    WHERE ap.is_active = '{is_active}'
    GROUP BY ap.id, ap.is_active
    ORDER BY questions_answered DESC
    LIMIT {limit}
    """
    try:
        result = run_athena_query(query)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))