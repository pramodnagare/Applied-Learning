**Aim:** Employee Retention Tool Kit

**Description:** This project is aim to develope machine learning models that can help human resource team to predict whether or not given employee will leave the company in coming days. If yes, then HR Team can take relative measures to prevent the situation as per the requirement.

**Tags:** **classification**, **imbalanced-dataset**, **scaling**, **sampling**, **tableau-dashboards**

**Dataset:** Avaialable on Kaggle: https://www.kaggle.com/gummulasrikanth/hr-employee-retention

**Python Implementation:** ToolKit.ipynd

**Model Analysis:** 

[Interactive Dashboard Avaiable here](https://public.tableau.com/profile/pramod.nagare#!/vizhome/EmployeeRetentionToolKitModelPerformanceAnalysis1/ModelAnalysis)

<img src= Model%20Analysis/Model%20Analysis%201.png>

### Observations:

1. Random Forest and Decision Tree are performed for Recall and Precision
2. There is very less but positve impact of feature normalization on Random Forest and Decision Tree models
3. MLP model is sensitive to feature normalization, it performed better with scaled features
4. GaussianNB is the fastest of all models, however, it has the worst accuracy

### Model Performance Analysis with fearture selection:

From EDA, we observed that department of an employee is less significant for employee leaving or not. So, to back our observation, we can dropped department features from our dataset and developed models.

[Interactive Dashboard Avaiable here](https://public.tableau.com/profile/pramod.nagare#!/vizhome/EmployeeRetentionToolKitModelPerformanceAnalysis2/ModelAnalysis)

<img src= Model%20Analysis/Model%20Analysis%202.png>

### Observations:

1. After training our models on selective features, model performance increased in all aspects
2. MLP and Logistic Regression models are faster than previous attempt as less number of features
3. MLP model is sensitive to feature normalization, it performed better with scaled features
4. RF, DT, and MLP are top-performing modelsFeature selection and engineering is the most critical step in ML model development


### Conclusion:

1. Feature selection and feature engineering is the most important step in the ML model design
2. Exploratory Data Analysis can lead us to take proper assumption while performing feature engineering and selection 
3. Feature normalization is one of the best practice to avoid biasing in model training
4. For the imbalanced dataset,sampling of data must be performed, otherwise, the model won't be reliable
