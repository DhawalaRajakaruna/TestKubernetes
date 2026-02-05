from pathlib import Path
from fastapi import FastAPI, Depends, Request,HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.staticfiles import StaticFiles
from app.database import engine, Base, get_db

from app.schemas.student import StudentCreate, StudentUpdate
from app.schemas.admin import AdminLogin

from app.crud import student as student_crud
from app.crud import admin as admin_crud
from app.crud import subject as subject_crud
from app.crud import initialize_default_data

# Middleware for session management
from starlette.middleware.sessions import SessionMiddleware
from fastapi import Request, HTTPException, status

app = FastAPI()

#just for future use cases like flash messages , user sessions etc.
app.add_middleware(
    SessionMiddleware, 
    secret_key="A7x9K2mP5qR8sT1vW4yZ7bC0dF3gH6jL9nM2pQ5rS8tU1vX4wY7zA0bC3dE6fG"#just a random string
)

#Create all the database tables when it starts
@app.on_event("startup")# make it run when application starts 
async def on_startup():
    async with engine.begin() as conn:
        print("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully.")   

    await initialize_default_data()



# Get the directory where main.py is located
BASE_DIR = Path(__file__).resolve().parent

# Initialize Jinja2 templates with absolute path
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

#No need of having satics files for now
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")



def admin_required(request: Request):
    if not request.session.get("admin_id"):
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/"}
        )


    
def control_cache(request: Request, html: HTMLResponse):
    html.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    html.headers["Pragma"] = "no-cache"
    html.headers["Expires"] = "0"
    return html

# @app.get("/dashboard", dependencies=[Depends(admin_required)])
# async def dashboard(request: Request):
#     admin_id = request.session.get("admin_id")
#     username = request.session.get("name")
#     html = templates.TemplateResponse("dashboard.html", {"request": request, "username": username})
#     return control_cache(request, html)

@app.get("/dashboard", dependencies=[Depends(admin_required)])
async def dashboard(request: Request):
    html = templates.TemplateResponse(
        "dashboard.html",
        {"request": request,"username": request.session.get("name")}
    )
    return control_cache(request, html)

######################### Home Page ######################
# @app.get("/", response_class=HTMLResponse, dependencies=[Depends(admin_required)])
# async def home(request: Request):
#     html = templates.TemplateResponse("auth/index.html", {"request": request})
#     return control_cache(request, html)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("auth/index.html", {"request": request})



#Done
######################## View Student List Page ######################
@app.get("/stdlist", response_class=HTMLResponse,dependencies=[Depends(admin_required)])
async def stdlist_page(request: Request):
    html = templates.TemplateResponse("students/stdlist.html", {"request": request})
    return control_cache(request, html)

@app.get("/get-all-students", response_class=JSONResponse)
async def get_all_students(db: AsyncSession = Depends(get_db)):
    students = await student_crud.get_students(db)
    return JSONResponse(content=students)

@app.get("/get-all-subjects", response_class=JSONResponse)
async def get_all_subjects(db: AsyncSession = Depends(get_db)):
    subjects = await subject_crud.get_all_subjects(db)
    return JSONResponse(content=[{
        "sub_id": s.sub_id,
        "name": s.name,
        "description": s.description
    } for s in subjects])

@app.get("/get-students-by-mail", response_class=JSONResponse)
async def get_students_by_mail(email: str, db: AsyncSession = Depends(get_db)):
    student = await student_crud.get_student_by_email(db, email) #calling the crud function
    if student != None:
        return JSONResponse(content=student)
    else:
        return JSONResponse(content=None, status_code=404)


#Done
######################## Register Student Page ######################
@app.get("/registerstd", response_class=HTMLResponse, dependencies=[Depends(admin_required)])
async def registerstd_page(request: Request, db: AsyncSession = Depends(get_db)):
    subjects = await subject_crud.get_all_subjects(db)

    html = templates.TemplateResponse(
        "students/registerstd.html", 
        {"request": request, "subjects": subjects}
    )
    return control_cache(request, html)

@app.post("/submit-newstd")
async def submit_newstd(request: Request, db: AsyncSession = Depends(get_db)):
    admin_id = request.session.get("admin_id")
    try:
        form_data = await request.form()
        name = form_data.get("name")
        age = form_data.get("age")
        grade = form_data.get("grade")
        email = form_data.get("email")
        subjects = form_data.getlist("subjects")
        
        student_data = StudentCreate(
            name=name,
            age=int(age),
            grade=grade,
            email=email,
            subjects=subjects,
            admin_id=admin_id
        )
        
        result = await student_crud.create_student(db, student_data)
        
        if result is None:
            return JSONResponse({
                "message": "Error: Student with this email already exists!"
            }, status_code=400)
        
        return JSONResponse({
            "message": "Student registered successfully!",
            "student": {
                "name": result.name,      # Access as object attributes
                "age": result.age,        # not dictionary keys
                "grade": result.grade,
                "email": result.email,
            }
        })
    except Exception as e:
        print(f"Error in submit_newstd: {e}")
        return JSONResponse({
            "message": f"Error: {str(e)}"
        }, status_code=500)


#Done
######################## Delete Student Page ######################
@app.get("/deletestd", response_class=HTMLResponse, dependencies=[Depends(admin_required)])
async def deletestd_page(request: Request):
    html = templates.TemplateResponse("students/deletestd.html", {"request": request})
    return control_cache(request, html)


@app.post("/submit-delstd")
async def submit_delstd(request: Request, db: AsyncSession = Depends(get_db)):
    """Delete student by email"""
    try:
        data = await request.json()
        email = data.get("email")
        
        if not email:
            return JSONResponse(
                {"message": "Email is required"},
                status_code=400
            )
        await student_crud.delete_student_by_email(db, email)

        
    except Exception as e:
        print(f"Error deleting student: {e}")
        return JSONResponse(
            {"message": f"Error deleting student: {str(e)}"},
            status_code=500
        )
#Done
######################## Update Student Page ######################
@app.get("/updatestd", response_class=HTMLResponse, dependencies=[Depends(admin_required)])
async def updatestd_page(request: Request):
    html = templates.TemplateResponse("students/updatestd.html", {"request": request})
    return control_cache(request, html)

@app.post("/submit-updatestd")
async def submit_updatestd(request: Request, db: AsyncSession = Depends(get_db)):
    admin_id = request.session.get("admin_id")
    
    try:
        form_data = await request.form()
        id = form_data.get("id")
        name = form_data.get("name")
        age = form_data.get("age")
        grade = form_data.get("grade")
        email = form_data.get("email")
        subjects = form_data.getlist("subjects")
        
        if not all([id, name, age, grade, subjects]):
            return JSONResponse(
                {"error": "All fields are required and at least one subject must be selected!"},
                status_code=400
            )

        try:
            age_int = int(age)
            if age_int <= 0 or age_int > 150:
                return JSONResponse(
                    {"error": "Age must be between 1 and 150!"},
                    status_code=400
                )
        except ValueError:
            return JSONResponse(
                {"error": "Age must be a valid number!"},
                status_code=400
            )
        
        if not subjects or len(subjects) == 0:
            return JSONResponse(
                {"error": "Please select at least one subject to enroll!"},
                status_code=400
            )
        
        student_data = StudentUpdate(
            id=id,
            name=name,
            age=age_int,
            grade=grade,
            subjects=subjects,
            admin_id=admin_id
        )

        await student_crud.update_student(db, student_data)
        
        return JSONResponse(
            {"message": f"Student {name} updated successfully!"},
            status_code=200
        )
        
    except Exception as e:
        return JSONResponse(
            {"error": f"Error updating student: {str(e)}"},
            status_code=500
        )


######################## Login Page ######################
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})
    


@app.post("/submit-login", response_class=HTMLResponse)
async def submit_login(request: Request,db: AsyncSession = Depends(get_db)):
    try:
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")
        
        log_admin = AdminLogin(
            username=username, 
            password=password
            )
        
        isadmin = await admin_crud.login_admin(db, log_admin)

        if isadmin is None:
            return JSONResponse(
                content={"error": "Invalid username or password!"},
                status_code=401
            )
        
        # Use session to store admin info
        request.session["admin_logged_in"] = True
        request.session["admin_id"] = isadmin.admin_id if isadmin else None
        request.session["name"] = isadmin.name if isadmin else None

        
        html=templates.TemplateResponse("dashboard.html", {"request": request, "username": isadmin.name})
        return control_cache(request, html)
    except Exception as e:
        return JSONResponse(
            content={"error": f"Login failed: {str(e)}"},
            status_code=500
        )

# ######################## Manage Admin Page ######################
# @app.get("/manageadmin", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("admins/manageadmin.html", {"request": request})



# ####################### Manage Subject Page ######################
# @app.get("/managesubject", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("admins/managesubject.html", {"request": request})



###################### Logout Endpoint ######################
# @app.get("/logout")
# async def logout(request: Request):
#     request.session.clear()

#     response = RedirectResponse(url="/login", status_code=303)
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Pragma"] = "no-cache"
#     response.headers["Expires"] = "0"
#     return response

     
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    html= templates.TemplateResponse("auth/index.html", {"request": request})
    return control_cache(request, html)