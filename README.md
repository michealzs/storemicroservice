# AI Commerce Service

A FastAPI + LangChain/LangGraph commerce backend with a retrieval-augmented
shopping assistant, converted from the original Django `storemicroservice`
backend. The store's domain model (catalog, cart, orders, reviews, coupons) is
ported to async SQLAlchemy and re-exposed as a REST API, with a LangGraph agent
that answers shopper questions over the live catalog.

## Stack

| Concern        | Technology |
|----------------|------------|
| API            | FastAPI + Uvicorn |
| Data           | SQLAlchemy (async) + Postgres |
| Vector store   | **pgvector** (primary), Weaviate & Pinecone adapters (optional) |
| LLM / agents   | LangChain + LangGraph (`create_react_agent`) |
| Observability  | Langfuse + LangSmith |
| Payments       | Stripe (optional; checkout works offline without a key) |
| IaC            | Terraform (pgvector container, optional Pinecone index / Weaviate) |

## What was ported

- `backend/store/models.py` → `app/domain/models.py` (Category, Subcategory,
  Product, ProductVariant, ProductImage, ProductReview, Coupon, Cart, CartItem,
  Order) as SQLAlchemy models. `sale_price()` / `get_final_price()` preserved.
- `backend/store/views.py` REST surface → `app/api/routes_catalog.py` &
  `routes_cart.py` (products, detail, featured, categories, search, add-to-cart,
  checkout, reviews).
- The Django project/settings were removed. The static `frontend/` (plain
  HTML + axios) is kept; point its API base URL at this service.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz`, `/readyz` | Liveness / readiness |
| GET/POST | `/products` | List / create products |
| GET | `/products/{slug}` | Product detail |
| GET | `/featured-products` | Featured products |
| GET | `/categories`, `/category/{slug}` | Categories / products by category |
| GET | `/search?q=` | Catalog search |
| POST | `/cart/add/{slug}` | Add to cart |
| GET | `/cart/{session}` | View cart |
| POST | `/checkout/{session}` | Create order (Stripe when keyed) |
| POST | `/reviews/{slug}` | Submit a review |
| POST | `/ingest` | Embed catalog into the vector store |
| POST | `/chat` | RAG shopping assistant (LangGraph) |

## Run it

```bash
cp .env.example .env          # optionally add DEEPSEEK_API_KEY / STRIPE_SECRET_KEY
docker compose up -d --build
docker compose exec app python -m scripts.seed
curl -X POST localhost:8000/ingest
curl -X POST localhost:8000/chat -H 'content-type: application/json' \
     -d '{"message": "headphones for travel under $200"}'
```

Local dev: `make install && make test && make run`.

## Keyless operation

Runs end-to-end with no secrets: catalog/cart/checkout/reviews work as-is;
embeddings and the vector store fall back to offline implementations, and
`/chat` returns ranked catalog matches. Add `DEEPSEEK_API_KEY` (or `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`) for conversational answers, `STRIPE_SECRET_KEY` for real
payments, and Langfuse/LangSmith keys for tracing.

## Terraform

```bash
cd terraform && terraform init && terraform plan
terraform apply -var 'enable_pinecone=true'
```
