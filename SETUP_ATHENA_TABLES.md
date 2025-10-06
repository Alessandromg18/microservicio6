# 📋 Guía Paso a Paso: Crear Tablas en AWS Athena

## 🎯 Problema Actual
Tu microservicio está funcionando correctamente, pero las tablas no existen en Athena:
```
TABLE_NOT_FOUND: Table 'awsdatacatalog.scrapetok.scraped_acount' does not exist
TABLE_NOT_FOUND: Table 'awsdatacatalog.scrapetok.admin_profiles' does not exist
```

---

## 🚀 Solución: 3 Opciones

### **Opción 1: Crear Tablas desde AWS Console (Recomendado)**

#### Paso 1: Acceder a Athena
1. Ve a **AWS Console**: https://console.aws.amazon.com/athena/
2. Asegúrate de estar en la región **us-east-1**
3. Si es la primera vez, configura el bucket de resultados:
   - Settings → Manage
   - Query result location: `s3://mvanalitica/athena-results/`

#### Paso 2: Crear la Base de Datos
```sql
CREATE DATABASE IF NOT EXISTS scrapetok;
```

#### Paso 3: Ejecutar el Script de Creación
1. Abre el archivo `create_athena_tables.sql`
2. Copia el contenido completo
3. Pégalo en el Query Editor de Athena
4. Haz clic en **Run** (o presiona Ctrl+Enter)

#### Paso 4: Verificar las Tablas
```sql
SHOW TABLES IN scrapetok;
```

Deberías ver:
- `scraped_acount`
- `admin_profiles`
- `quest_and_answer`
- `admin_tiktok_metrics`
- `user_apify_filters`
- `user_apify_call_historial`

---

### **Opción 2: Crear Tablas con AWS CLI**

```bash
# 1. Crear la base de datos
aws athena start-query-execution \
  --query-string "CREATE DATABASE IF NOT EXISTS scrapetok" \
  --result-configuration "OutputLocation=s3://mvanalitica/athena-results/" \
  --region us-east-1

# 2. Crear las tablas (ejecuta el script completo)
aws athena start-query-execution \
  --query-string file://create_athena_tables.sql \
  --result-configuration "OutputLocation=s3://mvanalitica/athena-results/" \
  --query-execution-context "Database=scrapetok" \
  --region us-east-1
```

---

### **Opción 3: Crear con Datos de Ejemplo**

Si quieres probar rápidamente con datos de ejemplo:

#### Paso 1: Crea archivos CSV localmente

**scraped_acount.csv:**
```csv
id,userId,account_name,scraped_date,status
1,user123,tiktok_user_1,2025-01-15 10:30:00,active
2,user123,tiktok_user_2,2025-01-16 11:00:00,active
3,user123,tiktok_user_3,2025-01-17 09:45:00,active
4,user456,tiktok_user_4,2025-01-18 14:20:00,active
5,user456,tiktok_user_5,2025-01-19 16:30:00,active
```

**admin_profiles.csv:**
```csv
id,name,email,is_active,created_at
admin001,Juan Pérez,juan@scrapetok.com,true,2024-01-01 00:00:00
admin002,María García,maria@scrapetok.com,true,2024-01-15 00:00:00
admin003,Carlos López,carlos@scrapetok.com,false,2024-02-01 00:00:00
```

**quest_and_answer.csv:**
```csv
id,admin_id,question,answer,answered_at
q1,admin001,¿Cómo usar el scraper?,Sigue la guía...,2025-01-10 10:00:00
q2,admin001,¿Cuál es el límite?,El límite es 1000,2025-01-11 11:00:00
q3,admin002,¿Cómo exportar?,Usa el botón...,2025-01-12 12:00:00
```

**admin_tiktok_metrics.csv:**
```csv
id,adminid,video_id,views,likes,comments,shares,metric_date
m1,admin001,video123,15000,1200,340,89,2025-01-15 00:00:00
m2,admin001,video124,10000,850,220,45,2025-01-16 00:00:00
m3,admin002,video125,8500,720,180,32,2025-01-17 00:00:00
```

#### Paso 2: Subir a S3
```bash
aws s3 cp scraped_acount.csv s3://mvanalitica/scraped_acount/
aws s3 cp admin_profiles.csv s3://mvanalitica/admin_profiles/
aws s3 cp quest_and_answer.csv s3://mvanalitica/quest_and_answer/
aws s3 cp admin_tiktok_metrics.csv s3://mvanalitica/admin_tiktok_metrics/
```

#### Paso 3: Crear las tablas
Ejecuta el script `create_athena_tables.sql` en Athena Console

#### Paso 4: Verificar los datos
```sql
SELECT COUNT(*) FROM scrapetok.scraped_acount;
SELECT COUNT(*) FROM scrapetok.admin_profiles;
```

---

## ✅ Verificación Final

### 1. Prueba las Queries Directamente en Athena
```sql
-- Query 1: Usuarios con más cuentas scrapeadas
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
LIMIT 10;

-- Query 2: Admins con preguntas y vistas
SELECT
  ap.id AS admin_id,
  ap.is_active,
  COUNT(qa.id) AS questions_answered,
  COALESCE(AVG(atm.views), 0) AS avg_views
FROM admin_profiles ap
LEFT JOIN quest_and_answer qa ON qa.admin_id = ap.id
LEFT JOIN admin_tiktok_metrics atm ON atm.adminid = ap.id
WHERE ap.is_active = 'true'
GROUP BY ap.id, ap.is_active
ORDER BY questions_answered DESC
LIMIT 10;
```

### 2. Prueba tu Microservicio
```bash
# Endpoint 1
curl "http://localhost:8006/users/most_scraped?limit=5"

# Endpoint 2
curl "http://localhost:8006/admins/questions_and_views?is_active=true&limit=5"
```

### 3. Swagger UI
Abre http://localhost:8006/docs y prueba los endpoints desde ahí

---

## 🔍 Troubleshooting

### "Access Denied" al crear tablas
**Solución:** Verifica que tu usuario IAM tenga estos permisos:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "athena:*",
        "glue:*",
        "s3:GetBucketLocation",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:PutObject"
      ],
      "Resource": "*"
    }
  ]
}
```

### "Bucket does not exist"
**Solución:** Verifica que el bucket `mvanalitica` exista:
```bash
aws s3 ls s3://mvanalitica/
```

Si no existe, créalo:
```bash
aws s3 mb s3://mvanalitica --region us-east-1
```

### Las queries retornan 0 resultados
**Solución:** Las tablas están vacías. Necesitas:
1. Subir datos CSV a S3 (Opción 3 arriba)
2. O conectar tus tablas a datos existentes
3. O usar datos de producción si existen

---

## 📞 Siguiente Paso

Una vez que ejecutes el script `create_athena_tables.sql` en AWS Athena:

1. Las tablas se crearán
2. Tu microservicio podrá consultarlas
3. Los endpoints retornarán datos (si hay datos en las tablas)

**¿Listo para crear las tablas?** 🚀

1. Ve a https://console.aws.amazon.com/athena/
2. Copia el contenido de `create_athena_tables.sql`
3. Ejecuta en el Query Editor
4. ¡Listo! Tus endpoints funcionarán
