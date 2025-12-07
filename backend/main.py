from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse 
from fastapi.templating import Jinja2Templates 
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import database
from . import models
from . import schemas
from . import crud
from fastapi import Form
from fastapi.responses import RedirectResponse
from typing import Optional
import threading


app = FastAPI(title="Product Management API")

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_tables():
    try:
        models.Base.metadata.create_all(bind=database.engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")

# Create tables in a background thread to avoid blocking startup
table_creation_thread = threading.Thread(target=create_tables, daemon=True)
table_creation_thread.start()

app.mount("/static", StaticFiles(directory="static"), name="static")

Template = Jinja2Templates(directory="backend/templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    try:
        return {"message": "Product Management API is running!"}
    except Exception as e:
        print(f"Error in root endpoint: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# Category Routes
@app.post("/categories/", response_model=schemas.CategoryResponse)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db, category)

@app.get("/categories/", response_model=list[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)


# Product Routes
@app.post("/products/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_product(db, product) 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/products/", response_model=list[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return crud.get_products(db)

@app.get("/products/{product_id}", response_model=schemas.ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product_by_id(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    updated = crud.update_product(db, product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_product(db, product_id)
    if not deleted:

        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# Main endpoint to display products
@app.get("/main", response_class=HTMLResponse)
async def main_products(request: Request, db: Session = Depends(get_db)):
    products = crud.get_products(db)
    
    product_db = [
        {
            "request": request,
            "product_id": product.id, 
            "product_name": product.name,
            "product_description": product.description,
            "is_available": product.is_available,
            "product_category": product.category.name if product.category else "Uncategorized",
            "product_price": product.price,
            "product_quantity": product.quantity
        } for product in products
    ]
    
    
    return Template.TemplateResponse("index.html", {"request": request, "products": product_db})
#create add products endpoint
@app.get("/addProducts", response_class=HTMLResponse)
async def add_products(request: Request):
    return Template.TemplateResponse("addProducts.html", {"request": request})


# Fallback endpoint to accept form submissions (non-JS clients)
@app.post("/products/add")
async def add_product_form(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    quantity: int = Form(...),
    is_available: bool = Form(False),
    image_url: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
):
    try:
        product_in = schemas.ProductCreate(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            is_available=is_available,
            image_url=image_url,
            category_id=category_id,
        )
        crud.create_product(db, product_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return RedirectResponse(url="/main", status_code=303)

#creating categories 
@app.get("/createCategories", response_class=HTMLResponse)
async def create_categories(request: Request):
    return Template.TemplateResponse("createCategories.html", {"request": request})

@app.post("/categories/add")
async def add_category_form(
    category_name: str = Form(...),
    db: Session = Depends(get_db),
):
    
    try:
        category_in = schemas.CategoryCreate(name=category_name)
        crud.create_category(db, category_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return RedirectResponse(url="/createCategories", status_code=303)


