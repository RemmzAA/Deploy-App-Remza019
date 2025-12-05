from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Data models
class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    image: str
    technologies: List[str]
    category: str
    live_demo: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Service(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    features: List[str]
    price_range: str
    icon: str

class Testimonial(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    company: str
    role: str
    content: str
    rating: int
    avatar: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BlogPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    slug: str
    excerpt: str
    content: str
    author: str
    category: str
    tags: List[str]
    featured_image: str
    published: bool = True
    published_at: datetime = Field(default_factory=datetime.utcnow)

class ContactForm(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    company: Optional[str] = None
    subject: str
    message: str
    service_interest: Optional[str] = None
    budget_range: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

class FreelancerProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    title: str
    bio: str
    skills: List[str]
    portfolio_links: List[str]
    hourly_rate: str
    availability: str
    avatar: str
    featured: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Portfolio API endpoints
@api_router.get("/")
async def root():
    return {"message": "019 Digital Solutions API", "version": "2.0"}

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    """Get all portfolio projects"""
    projects_data = [
        {
            "id": str(uuid.uuid4()),
            "title": "Trading Intelligence Platform",
            "description": "Advanced fintech dashboard with real-time market data, AI-powered trading signals, subscription management, and comprehensive portfolio analytics.",
            "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=600&fit=crop",
            "technologies": ["React", "TypeScript", "Node.js", "WebSocket", "Stripe", "Alpaca API"],
            "category": "Fintech",
            "live_demo": "#portfolio",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Remza019 Gaming Website",
            "description": "Professional gaming platform showcasing YouTube channel content, stream schedules, and interactive community features with modern responsive design.",
            "image": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&h=600&fit=crop",
            "technologies": ["React", "CSS3", "JavaScript", "YouTube API"],
            "category": "Gaming",
            "live_demo": "#portfolio",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Adriatic Dreams Tourism",
            "description": "Elegant tourism showcase featuring luxury coastal experiences, interactive galleries, and seamless booking integration with stunning visual design.",
            "image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&h=600&fit=crop",
            "technologies": ["HTML5", "CSS3", "JavaScript", "Bootstrap"],
            "category": "Tourism",
            "live_demo": "#portfolio",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Berlin Apartment Booking",
            "description": "Sophisticated property booking system with advanced search filters, interactive maps, and streamlined reservation management.",
            "image": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop",
            "technologies": ["React", "Tailwind CSS", "API Integration", "MongoDB"],
            "category": "Real Estate",
            "live_demo": "#portfolio",
            "created_at": datetime.utcnow()
        }
    ]
    return [Project(**project) for project in projects_data]

@api_router.get("/services", response_model=List[Service])
async def get_services():
    """Get all services offered"""
    services_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Full-Stack Development",
            "description": "Complete web applications using modern frameworks like React, Node.js, and MongoDB",
            "features": ["Frontend & Backend Development", "Database Design", "API Integration", "Performance Optimization"],
            "price_range": "$2,000 - $15,000",
            "icon": "⟨/⟩"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Responsive Design",
            "description": "Mobile-first, responsive websites that work seamlessly across all devices",
            "features": ["Mobile Optimization", "Cross-browser Compatibility", "Modern UI/UX", "Accessibility Standards"],
            "price_range": "$800 - $5,000",
            "icon": "◈◇◈"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "E-commerce Solutions",
            "description": "Complete online stores with payment integration and inventory management",
            "features": ["Payment Gateway Integration", "Inventory Management", "Admin Dashboard", "SEO Optimization"],
            "price_range": "$3,000 - $20,000",
            "icon": "⟦$⟧"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Performance Optimization",
            "description": "Lightning-fast websites optimized for speed, SEO, and user experience",
            "features": ["Speed Optimization", "SEO Enhancement", "Code Splitting", "CDN Integration"],
            "price_range": "$500 - $3,000",
            "icon": "⚡◄►"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Gaming Solutions",
            "description": "Interactive gaming platforms, streaming sites, and community features",
            "features": ["Game Development", "Streaming Integration", "Community Platforms", "Real-time Features"],
            "price_range": "$1,500 - $10,000",
            "icon": "⟪◎⟫"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "AI Integration",
            "description": "Cutting-edge AI features, chatbots, and machine learning implementations",
            "features": ["AI Chatbots", "ML Models", "Data Analysis", "Automation"],
            "price_range": "$2,500 - $20,000",
            "icon": "⟨◉⟩"
        }
    ]
    return [Service(**service) for service in services_data]

@api_router.get("/testimonials", response_model=List[Testimonial])
async def get_testimonials():
    """Get client testimonials"""
    testimonials_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Marko Petrović",
            "company": "StartupTech Belgrade",
            "role": "CEO",
            "content": "019solutions je transformisao našu ideju u profitabilnu platformu za samo 4 nedelje! ROI od 300% u prvom mesecu lansiranja. Fenomenalni tim!",
            "rating": 5,
            "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=faces"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Ana Nikolić",
            "company": "Digital Boost Agency",
            "role": "Marketing Director", 
            "content": "Najbolja investicija koju smo napravili! Naša nova web aplikacija generiše 10x više leadova nego stara stranica. Profesionalizam na najvišem nivou.",
            "rating": 5,
            "avatar": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=faces"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Stefan Jovanović",
            "company": "InnovateLab",
            "role": "CTO",
            "content": "Izuzetna brzina isporuke i kvalitet koda! Uspeli su da implementiraju AI funkcionalnosti koje niko drugi nije mogao. Definitivno ću ih ponovo angažovati.",
            "rating": 5,
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=faces"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Milica Stojanović",
            "company": "E-commerce Solutions",
            "role": "Founder",
            "content": "Prodaja je porasla za 450% nakon što nam je 019solutions redizajnirao online prodavnicu. Svaki evro uložen se vratio desetostruko!",
            "rating": 5,
            "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=faces"
        }
    ]
    return [Testimonial(**testimonial) for testimonial in testimonials_data]

@api_router.get("/blog", response_model=List[BlogPost])
async def get_blog_posts():
    """Get blog posts"""
    blog_posts = [
        {
            "id": str(uuid.uuid4()),
            "title": "The Future of Web Development in 2025",
            "slug": "future-web-development-2025",
            "excerpt": "Exploring emerging technologies and trends that will shape web development in the coming year.",
            "content": "Full article content here...",
            "author": "019solutions",
            "category": "Technology",
            "tags": ["Web Development", "Trends", "2025"],
            "featured_image": "https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=800&h=400&fit=crop",
            "published": True,
            "published_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Building High-Performance React Applications",
            "slug": "high-performance-react-apps",
            "excerpt": "Best practices for optimizing React applications for speed and user experience.",
            "content": "Full article content here...",
            "author": "019solutions",
            "category": "Development",
            "tags": ["React", "Performance", "Optimization"],
            "featured_image": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&h=400&fit=crop",
            "published": True,
            "published_at": datetime.utcnow()
        }
    ]
    return [BlogPost(**post) for post in blog_posts]

@api_router.get("/freelancers", response_model=List[FreelancerProfile])
async def get_freelancers():
    """Get featured freelancer profiles"""
    freelancers_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Alex Thompson",
            "title": "Full-Stack Developer",
            "bio": "Experienced developer specializing in React and Node.js with 5+ years of experience building scalable web applications.",
            "skills": ["React", "Node.js", "MongoDB", "TypeScript", "AWS"],
            "portfolio_links": ["https://alexthompson.dev", "https://github.com/alexthompson"],
            "hourly_rate": "$75-100/hour",
            "availability": "Available",
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=faces",
            "featured": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Maria García",
            "title": "UI/UX Designer",
            "bio": "Creative designer focused on user-centered design and modern interface solutions for web and mobile applications.",
            "skills": ["Figma", "Adobe Creative Suite", "Prototyping", "User Research", "Responsive Design"],
            "portfolio_links": ["https://mariagarcia.design", "https://dribbble.com/mariagarcia"],
            "hourly_rate": "$60-85/hour",
            "availability": "Available",
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=faces",
            "featured": True
        }
    ]
    return [FreelancerProfile(**freelancer) for freelancer in freelancers_data]

@api_router.post("/contact", response_model=ContactForm)
async def submit_contact_form(contact_data: ContactForm):
    """Submit contact form"""
    try:
        # Save to database
        contact_dict = contact_data.dict()
        await db.contact_forms.insert_one(contact_dict)
        return contact_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit contact form: {str(e)}")

@api_router.get("/stats")
async def get_company_stats():
    """Get company statistics"""
    return {
        "projects_completed": 75,
        "happy_clients": 58, 
        "years_experience": 6,
        "technologies_mastered": 35,
        "team_members": 12,
        "countries_served": 18,
        "client_satisfaction": "98.7%",
        "avg_project_delivery": "3.2 weeks",
        "avg_roi_increase": "285%",
        "repeat_clients": "87%"
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - 019solutions - %(levelname)s - %(message)s'
)
logger = logging.getLogger("019solutions")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()