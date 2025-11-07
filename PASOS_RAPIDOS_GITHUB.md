# Pasos Rápidos: Subir Código a tu Repo de GitHub

## ✅ Tu Situación
- ✅ Repositorio ya creado en GitHub: `prueba-tecnica-ani-scraping`
- ✅ Código local listo para subir
- ⚠️ Necesitas conectar y subir

---

## 🚀 Opción 1: GitHub Desktop (MÁS FÁCIL - Recomendado)

### Paso 1: Instalar GitHub Desktop
1. Descarga: https://desktop.github.com/
2. Instala y abre
3. Login con tu cuenta GitHub (ArtDeros)

### Paso 2: Agregar tu Carpeta Local
1. En GitHub Desktop: **File** → **Add Local Repository**
2. Click en **"Choose..."**
3. Selecciona: `C:\Users\Oscar Abella\Documents\AI\Prueba dapper\prueba_tecnica_DE_Dapper`
4. Click en **"Add repository"**

### Paso 3: Conectar con tu Repo de GitHub
1. En GitHub Desktop, arriba verás un botón **"Publish repository"** o **"Push origin"**
2. Si dice "Publish repository":
   - Click en el botón
   - **Nombre**: `prueba-tecnica-ani-scraping`
   - **Account**: ArtDeros
   - Desmarca "Keep this code private" si quieres que sea público
   - Click en **"Publish repository"**
3. Si ya está conectado, solo haz click en **"Push origin"**

### Paso 4: Hacer Commit y Push
1. En la pestaña **"Changes"** verás todos tus archivos
2. Abajo, escribe el mensaje:
   ```
   Initial commit: Pipeline de scraping ANI con Airflow
   ```
3. Click en **"Commit to main"**
4. Click en **"Push origin"** (arriba)

### ✅ ¡Listo!
Tu código ya está en: https://github.com/ArtDeros/prueba-tecnica-ani-scraping

---

## 💻 Opción 2: Git desde Terminal

### Paso 1: Instalar Git
1. Descarga: https://git-scm.com/download/win
2. Instala con opciones por defecto
3. **Reinicia VS Code/Cursor**

### Paso 2: Abrir Terminal Nueva
En VS Code/Cursor, abre una nueva terminal (Ctrl + `)

### Paso 3: Ejecutar Comandos
Ejecuta estos comandos **UNO POR UNO**:

```bash
# 1. Inicializar Git
git init

# 2. Agregar todos los archivos
git add .

# 3. Hacer commit
git commit -m "Initial commit: Pipeline de scraping ANI con Airflow"

# 4. Conectar con tu repo de GitHub
git remote add origin https://github.com/ArtDeros/prueba-tecnica-ani-scraping.git

# 5. Cambiar a rama main
git branch -M main

# 6. Subir a GitHub
git push -u origin main
```

### Si te pide autenticación:
- **Usuario**: `ArtDeros`
- **Contraseña**: Necesitas un **Personal Access Token** (ver abajo)

---

## 🔑 Crear Personal Access Token (si Git te lo pide)

GitHub ya no acepta contraseñas normales. Necesitas un Token:

1. Ve a: https://github.com/settings/tokens
2. Click en **"Generate new token"** → **"Generate new token (classic)"**
3. **Nombre**: "Prueba Tecnica" (o el que quieras)
4. **Expiración**: 90 días (o más)
5. **Permisos**: Marca solo `repo` (todos los permisos de repositorio)
6. Click en **"Generate token"**
7. **COPIA EL TOKEN** (solo se muestra una vez - guárdalo bien)
8. Cuando Git te pida contraseña, usa este token en lugar de tu contraseña

---

## ✅ Verificación

Después de subir, ve a:
```
https://github.com/ArtDeros/prueba-tecnica-ani-scraping
```

Debes ver:
- ✅ Todos tus archivos
- ✅ README.md formateado
- ✅ Estructura de carpetas (dags/, src/, configs/, sql/)

---

## 🆘 Si tienes Problemas

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/ArtDeros/prueba-tecnica-ani-scraping.git
```

### Error: "failed to push some refs"
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### No aparece "Publish repository" en GitHub Desktop
- Significa que ya está conectado
- Solo haz commit y push

---

## 📝 Resumen

**Opción más fácil**: GitHub Desktop
1. Instalar GitHub Desktop
2. Agregar carpeta local
3. Conectar con repo de GitHub
4. Commit y Push

**Opción con más control**: Git desde terminal
1. Instalar Git
2. Ejecutar los 6 comandos de arriba
3. Usar Personal Access Token si lo pide

---

**¿Cuál opción prefieres? Te guío paso a paso** 🚀

