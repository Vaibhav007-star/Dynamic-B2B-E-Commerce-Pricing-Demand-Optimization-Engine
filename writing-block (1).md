# MASTER PROMPT: Dynamic B2B E-Commerce Pricing & Demand Optimization Engine

## 1. Project Role and Objective

Act as a senior Data Scientist, Machine Learning Engineer, Backend Developer, Business Intelligence Analyst, and Cloud Solution Architect.

Build a practical, end-to-end project named:

**Dynamic B2B E-Commerce Pricing & Demand Optimization Engine**

The system should help a B2B retail, wholesale, or logistics business make better pricing decisions by analyzing historical sales, demand patterns, seasonal trends, product costs, competitor prices, and supply-related factors.

The primary goal is to forecast product demand, recommend profitable prices, and measure the business impact of optimized pricing against a static pricing baseline.

Work inside my existing VS Code environment using Antigravity. Inspect my current project files and installed tools before making changes.

## 2. Important Development Instructions

Follow these rules throughout development:

1. Start by inspecting the existing workspace, project files, installed dependencies, Python environment, and available datasets.
2. First provide a simple project plan and recommended architecture. Do not immediately generate the entire application.
3. Divide development into small, manageable phases.
4. Explain what each phase does in simple language.
5. Implement and test one phase at a time.
6. Do not delete, overwrite, or restructure existing files without checking their purpose.
7. Reuse existing datasets and code wherever appropriate.
8. If information is missing, make reasonable assumptions, clearly document them, and continue where possible.
9. Do not claim that a model, API, dashboard, or cloud deployment works unless it has actually been tested.
10. Do not expose API keys, passwords, or other secrets in source code.
11. Keep the project suitable for a student portfolio, technical demonstration, and business case study.
12. Do not introduce unnecessary complexity or paid services when a free local alternative is sufficient.

## 3. Phase 1 — Data Collection and Exploration

First, inspect whether the workspace already contains datasets.

If no suitable dataset exists, recommend and use a relevant publicly available dataset from sources such as Kaggle, UCI Machine Learning Repository, or other reputable open-data providers.

Prefer real historical retail, wholesale, or e-commerce transaction data. Do not fabricate a dataset and describe it as real.

Look for fields such as:

- Order date and product ID
- Product category and quantity sold
- Selling price and unit cost
- Revenue and gross profit
- Discounts and promotions
- Inventory or stock availability
- Competitor price, when available
- Seasonality and calendar features
- Region, customer segment, or sales channel

Not every dataset will contain every field. Document missing fields and their implications.

Tasks:
- Load the dataset using Pandas.
- Inspect columns, data types, missing values, duplicate rows, and outliers.
- Analyze historical sales, prices, demand, revenue, and gross margins.
- Identify seasonal patterns and product-level differences.
- Create charts that explain the business problem.
- Avoid data leakage when preparing training and test datasets.

Deliverables:
- Data quality report
- Exploratory data analysis notebook or Python scripts
- Business insights and documented assumptions

## 4. Phase 2 — Demand Forecasting

Develop a machine learning model to predict future product demand.

Preferred algorithms:
- XGBoost
- LightGBM
- Baseline model using historical averages or a simple forecasting method

Select the algorithm according to the dataset size, data quality, and installed dependencies. If XGBoost or LightGBM is unavailable, choose a suitable alternative.

Create useful features where supported by the data:
- Day, week, month, and season
- Historical demand and lag features
- Rolling demand averages
- Previous selling prices and discounts
- Product and category information
- Promotions, competitor prices, and stock availability

Use chronological training and test splits for time-dependent data.

Evaluate performance using appropriate metrics such as:
- MAE
- RMSE
- WAPE or another suitable demand-weighted metric

Explain why the selected model performs better than the baseline. Do not report invented accuracy scores.

Deliverables:
- Trained forecasting model
- Reproducible training script
- Evaluation report
- Demand predictions by product and forecast period

## 5. Phase 3 — Dynamic Pricing Optimization

Develop a pricing recommendation engine that aims to maximize gross profit or gross margin dollars while considering demand, costs, business constraints, and market conditions.

Start with a transparent optimization algorithm before considering reinforcement learning.

The initial optimizer should:
1. Generate a reasonable candidate price range for each product.
2. Estimate demand at candidate prices using a validated demand-response model.
3. Calculate expected revenue and gross profit.
4. Select the best feasible price under defined business constraints.
5. Compare the optimized decision with the static-price baseline.

Use the following basic calculations:

Revenue = Selling Price × Units Sold

Gross Profit = (Selling Price − Unit Cost) × Units Sold

Gross Margin Percentage = Gross Profit ÷ Revenue × 100

Expected Gross Profit = (Candidate Price − Unit Cost) × Predicted Demand at Candidate Price

Consider constraints such as:
- Minimum and maximum selling prices
- Minimum gross margin
- Competitor-price limits, if available
- Inventory availability
- Maximum allowed price changes
- Business-specific pricing rules

Important:
- A demand forecasting model alone does not prove how demand changes when price changes.
- Use observed price variation or a suitable price-elasticity model where the data supports it.
- Clearly identify assumptions and limitations when causal price-response data is unavailable.
- Do not recommend prices below cost unless an explicitly authorized business rule permits it.
- Treat competitor prices and supply disruptions as optional features when suitable data is available.

After the initial optimizer works, evaluate whether reinforcement learning adds genuine value. Only implement it if the available data and simulation environment support a meaningful experiment. Do not claim real-world revenue improvements from a simulated policy without validation.

Deliverables:
- Pricing optimization module
- Recommended price by product
- Predicted demand, revenue, and gross profit
- Explanation of the selected price
- Constraint and safety checks

## 6. Phase 4 — Static Baseline and Business Impact

Create a fair comparison between:

A. Static Pricing Strategy  
B. Optimized Pricing Strategy

Use the same evaluation period, product coverage, unit-cost assumptions, and demand conditions wherever possible.

Calculate:
- Baseline revenue
- Optimized revenue
- Baseline gross profit
- Optimized gross profit
- Revenue difference
- Gross profit difference
- Relative percentage changes
- Units sold and average selling price
- Margin percentage
- Product-level and category-level performance

Use clear formulas:

Revenue Change = Optimized Revenue − Baseline Revenue

Gross Profit Change = Optimized Gross Profit − Baseline Gross Profit

Relative Gross Profit Improvement (%) = (Optimized Gross Profit − Baseline Gross Profit) ÷ Baseline Gross Profit × 100

Handle zero denominators safely and label negative results honestly.

Do not use the phrase "revenue saved" when the result represents additional revenue or estimated uplift. Distinguish actual historical results from backtested estimates and simulated outcomes.

Avoid claiming that the optimized strategy caused an improvement unless the evaluation design supports that conclusion.

## 7. Phase 5 — FastAPI Backend

Build a clean REST API using FastAPI.

Suggested endpoints:

- GET /health — service health status
- GET /products — available products
- POST /forecast — generate demand forecasts
- POST /pricing/recommend — recommend prices
- GET /pricing/results — retrieve saved pricing results
- GET /business/impact — return baseline-versus-optimized metrics

Requirements:
- Validate requests with Pydantic.
- Return consistent JSON responses.
- Handle missing or invalid product IDs.
- Handle invalid prices, costs, and quantities.
- Load trained models safely.
- Keep business logic separate from API routes.
- Add useful error messages and logging.
- Provide interactive API documentation through FastAPI.
- Add automated tests for key calculations and endpoints.

Create a requirements.txt file and clear setup instructions.

Never expose a development server publicly without appropriate security and deployment configuration.

## 8. Phase 6 — Tableau or Power BI Dashboard

First inspect which BI tool is available in my environment.

If Tableau Public is available, prioritize Tableau Public and prepare clean CSV files or other supported data sources for dashboard development.

If Power BI is available and appropriate, use it as an alternative.

Do not assume Antigravity can directly control every desktop BI application. If direct interaction is unavailable, generate the required datasets, dashboard specifications, calculated fields, and step-by-step instructions for completing the dashboard in the installed tool.

Design a professional, executive-level dashboard with the following sections.

### Executive Overview
- Total baseline revenue
- Optimized or estimated revenue
- Baseline gross profit
- Optimized gross profit
- Gross profit improvement percentage
- Number of products analyzed

### Demand Forecasting
- Actual versus predicted demand
- Demand trends over time
- Seasonal demand patterns
- Forecast errors

### Pricing Optimization
- Current price versus recommended price
- Product-level expected demand
- Expected gross profit by product
- Competitor price comparison, when available
- Products requiring pricing review

### Business Impact
- Static strategy versus optimized strategy
- Revenue and gross profit comparisons
- Category-level performance
- Product-level winners and underperformers
- Historical versus forecast or simulated outcomes

Add useful filters for date, product, category, region, and pricing scenario wherever the dataset supports them.

Use a clean, readable layout suitable for a CEO or business manager.

Clearly label all simulated and backtested values. Do not present forecasts as realized financial results.

## 9. Phase 7 — Cloud Architecture

Create a practical AWS or Azure deployment design for the application.

Explain how the system could scale using services appropriate to the selected cloud platform.

For AWS, consider:
- Amazon ECS or another suitable container hosting option
- Amazon ECR for container images
- Application Load Balancer
- Auto Scaling
- Amazon S3 for datasets and model artifacts
- CloudWatch for monitoring
- IAM for access control

For Azure, consider:
- Azure Container Apps or another suitable hosting option
- Azure Container Registry
- Azure Blob Storage
- Azure Monitor
- Managed identity and access control

Choose one primary architecture and explain the alternative briefly.

Provide:
- Architecture diagram
- Data-flow explanation
- API deployment approach
- Scaling strategy
- Security considerations
- Monitoring approach
- Estimated cost factors and ways to minimize cost

Start with local deployment. Cloud deployment must be optional and should not incur charges without my explicit approval.

Do not claim that cloud resources have been deployed unless deployment has actually occurred.

## 10. Phase 8 — Testing and Reliability

Test the project end to end.

Verify:
- Dataset loading and validation
- Model training and inference
- Forecast evaluation
- Pricing optimization constraints
- Gross profit and revenue calculations
- Baseline comparison
- API input validation and responses
- Dashboard export files
- Reproducibility of results

Include tests for edge cases such as:
- Missing values
- Zero demand
- Zero revenue
- Invalid prices
- Missing cost data
- Products with insufficient history
- Negative or implausible predictions

Use a fallback strategy when model predictions or required data are unavailable.

Do not automatically apply recommended prices to a live business. The first version should provide recommendations for human review.

## 11. Suggested Project Structure

Use this structure as a starting point, adapting it to the existing workspace instead of blindly replacing files.

dynamic-pricing-engine/
    data/
        raw/
        processed/
        outputs/
    notebooks/
        exploratory_analysis.ipynb
    models/
    src/
        data/
        forecasting/
        optimization/
        evaluation/
        api/
    tests/
    dashboard/
    deployment/
    requirements.txt
    README.md
    .env.example

Do not commit confidential data, secrets, or unnecessarily large model artifacts.

## 12. Final Deliverables

By the end of development, aim to produce:

1. A documented, credible dataset and data quality report.
2. A reproducible demand forecasting model.
3. A pricing optimization engine with explicit constraints.
4. A fair static-versus-optimized business evaluation.
5. A working FastAPI service.
6. Clean dashboard-ready datasets.
7. A Tableau Public or Power BI dashboard plan and implementation guide.
8. A cloud architecture diagram and deployment instructions.
9. Automated tests and a README.
10. A project demonstration explaining the business problem, methodology, results, limitations, and future improvements.

## 13. Start Here

Do not begin by building everything at once.

First:
1. Inspect the VS Code workspace and installed tools.
2. Identify the available dataset and BI application.
3. Explain the project architecture in simple language.
4. Recommend the first development phase.
5. List the files you intend to create or modify.

Wait for my approval before proceeding to the next major phase. Once approved, implement the phase, run the relevant tests, and report the actual results before continuing.

The final goal is a reliable, explainable, portfolio-quality pricing optimization project that demonstrates machine learning, business decision-making, API development, business intelligence, and cloud architecture without inventing results or overstating model performance.