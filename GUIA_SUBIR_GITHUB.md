# Guía Paso a Paso: Subir Proyecto a GitHub

## 🔍 Paso 0: Verificar si tienes Git

Si Git no está instalado, tienes 2 opciones:

### Opción A: Instalar Git (Recomendado)
1. Descargar Git: https://git-scm.com/download/win
2. Instalar con opciones por defecto
3. Reiniciar la terminal/VS Code

### Opción B: Usar GitHub Desktop (Más Fácil)
1. Descargar: https://desktop.github.com/
2. Instalar y hacer login con tu cuenta de GitHub
3. Más fácil para principiantes

---

## 📋 PASO A PASO (Opción A: Git desde Terminal)

### Paso 1: Instalar Git (si no lo tienes)

1. Ve a: https://git-scm.com/download/win
2. Descarga el instalador
3. Ejecuta el instalador con opciones por defecto
4. **Reinicia VS Code o Cursor** después de instalar

### Paso 2: Verificar que Git funciona

Abre una nueva terminal en VS Code/Cursor y ejecuta:

```bash
git --version
```

Debe mostrar algo como: `git version 2.x.x`

### Paso 3: Configurar Git (solo primera vez)

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@ejemplo.com"
```

### Paso 4: Inicializar el Repositorio

```bash
# Asegúrate de estar en el directorio del proyecto
cd "C:\Users\Oscar Abella\Documents\AI\Prueba dapper\prueba_tecnica_DE_Dapper"

# Inicializar Git
git init
```

### Paso 5: Verificar qué archivos se van a subir

```bash
# Ver estado
git status
```

Debe mostrar todos los archivos del proyecto en verde (staged) o rojo (sin agregar).

### Paso 6: Agregar todos los archivos

```bash
# Agregar todos los archivos (el .gitignore excluirá los que no deben subirse)
git add .
```

### Paso 7: Hacer el Primer Commit

```bash
git commit -m "Initial commit: Pipeline de scraping ANI con Airflow

- Módulos de extracción, validación y escritura
- DAG de Airflow con 3 tareas en secuencia
- Reglas de validación configurables (YAML)
- Script SQL para crear tablas
- README con instrucciones de ejecución
- Idempotencia implementada"
```

### Paso 8: Crear Repositorio en GitHub

1. **Ir a GitHub**: https://github.com
2. **Hacer login** con tu cuenta
3. **Crear nuevo repositorio**:
   - Click en el botón "+" (arriba derecha)
   - Seleccionar "New repository"
   - **Nombre del repositorio**: `prueba-tecnica-ani-scraping` (o el que prefieras)
   - **Descripción**: "Pipeline de datos para extraer, validar y almacenar normativas de ANI usando Airflow"
   - **Visibilidad**: Público o Privado (tu elección)
   - ⚠️ **NO marques** "Add a README file" (ya tenemos uno)
   - ⚠️ **NO marques** "Add .gitignore" (ya tenemos uno)
   - ⚠️ **NO marques** "Choose a license"
   - Click en **"Create repository"**

### Paso 9: Copiar la URL del Repositorio

Después de crear el repo, GitHub te mostrará una página con instrucciones. **Copia la URL** que aparece, será algo como:

```
https://github.com/TU_USUARIO/prueba-tecnica-ani-scraping.git
```

### Paso 10: Conectar tu Repositorio Local con GitHub

```bash
# Reemplaza TU_USUARIO y NOMBRE_REPO con los tuyos
git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git

# Verificar que se agregó correctamente
git remote -v
```

### Paso 11: Cambiar a rama main (si es necesario)

```bash
git branch -M main
```

### Paso 12: Subir el Código a GitHub

```bash
git push -u origin main
```

**Si te pide usuario y contraseña:**
- Usuario: Tu usuario de GitHub
- Contraseña: Necesitarás un **Personal Access Token** (ver abajo)

### Paso 13: Verificar en GitHub

1. Ve a tu repositorio en GitHub
2. Debe mostrar todos los archivos
3. El README debe aparecer formateado en la página principal

---

## 🔑 Si te pide autenticación (Personal Access Token)

GitHub ya no acepta contraseñas normales. Necesitas un Token:

1. Ve a: https://github.com/settings/tokens
2. Click en "Generate new token" → "Generate new token (classic)"
3. **Nombre**: "Prueba Tecnica" (o el que quieras)
4. **Expiración**: 90 días (o más)
5. **Permisos**: Marca solo `repo` (todos los permisos de repositorio)
6. Click en "Generate token"
7. **COPIA EL TOKEN** (solo se muestra una vez)
8. Úsalo como contraseña cuando Git te la pida

---

## 📋 PASO A PASO (Opción B: GitHub Desktop - MÁS FÁCIL)

### Paso 1: Instalar GitHub Desktop

1. Descargar: https://desktop.github.com/
2. Instalar y abrir
3. Hacer login con tu cuenta de GitHub

### Paso 2: Agregar el Repositorio

1. En GitHub Desktop, click en **"File"** → **"Add Local Repository"**
2. Click en **"Choose..."** y selecciona la carpeta:
   ```
   C:\Users\Oscar Abella\Documents\AI\Prueba dapper\prueba_tecnica_DE_Dapper
   ```
3. Click en **"Add repository"**

### Paso 3: Hacer Commit

1. En la pestaña **"Changes"** verás todos los archivos
2. En el cuadro de abajo, escribe un mensaje:
   ```
   Initial commit: Pipeline de scraping ANI con Airflow
   ```
3. Click en **"Commit to main"**

### Paso 4: Publicar en GitHub

1. Click en el botón **"Publish repository"** (arriba)
2. **Nombre**: `prueba-tecnica-ani-scraping`
3. **Descripción**: "Pipeline de datos para extraer, validar y almacenar normativas de ANI usando Airflow"
4. Marca o desmarca "Keep this code private" según prefieras
5. Click en **"Publish repository"**

### Paso 5: ¡Listo!

El repositorio ya está en GitHub. Puedes verlo en tu perfil.

---

## ✅ Verificación Final

Después de subir, verifica:

- [ ] Todos los archivos están en GitHub
- [ ] El README se ve formateado correctamente
- [ ] No hay archivos sensibles (logs, __pycache__, etc.)
- [ ] El link del repositorio funciona

---

## 🔗 Tu Link del Repositorio

Una vez subido, tu link será:

```
https://github.com/TU_USUARIO/NOMBRE_REPO
```

**Ejemplo:**
```
https://github.com/oscar-abella/prueba-tecnica-ani-scraping
```

---

## 🆘 Si tienes Problemas

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git
```

### Error: "failed to push some refs"
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### No recuerdo mi usuario de GitHub
- Ve a: https://github.com/settings/profile
- Tu usuario aparece en la URL o en tu perfil

---

## 📝 Resumen de Comandos (Opción A)

```bash
# 1. Inicializar
git init
git add .
git commit -m "Initial commit: Pipeline ANI scraping con Airflow"

# 2. Conectar con GitHub (reemplaza TU_USUARIO y NOMBRE_REPO)
git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git
git branch -M main
git push -u origin main
```

---

**¿Necesitas ayuda con algún paso específico?** 🚀

