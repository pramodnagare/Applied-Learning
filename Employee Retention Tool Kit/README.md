**Aim:** Employee Retention Tool Kit

**Description:** This project is aim to develope machine learning models that can help human resource team to predict whether or not given employee will leave the company in coming days. If yes, then HR Team can take relative measures to prevent the situation as per the requirement.

**Tags:** **classification**, **imbalanced-dataset**, **scaling**, **sampling**, **tableau-dashboards**

**Dataset:** Avaialable on Kaggle: https://www.kaggle.com/gummulasrikanth/hr-employee-retention

**Python Implementation:** ToolKit.ipynd

**Model Analysis:** 

[Interactive Dashboard Avaiable here](https://public.tableau.com/profile/pramod.nagare#!/vizhome/EmployeeRetentionToolKitModelPerformanceAnalysis1/ModelAnalysis)

<img src= Model%20Analysis/Model%20Analysis%201.png>

### Observations:

1. Random Forest and Decision Tree are performed best with respect to Recall and Precision
2. There is very less impact of normalization on Random Forest and Decision Tree models
3. MLP model is sensitive to feature normalization, it performed better with scaled features
4. GaussianNB is fastest of all models, however, accuracy is the worst.

[Interactive Dashboard Avaiable here](https://public.tableau.com/profile/pramod.nagare#!/vizhome/EmployeeRetentionToolKitModelPerformanceAnalysis2/ModelAnalysis)

<img src= Model%20Analysis/Model%20Analysis%202.png>

### Observations:

1. After training our models on selective features, model performance increased in all aspects
2. MLP and Logistic Regression models are faster than previous attempt as less number of features
3. MLP model is sensitive to feature normalization, it performed better with scaled features
4. RF, DT and MLP are top performing models
5. Feature selection and engineering is the most critical step in ML model developement


# Conclusion:

1. Feature selection and feature engineering is most important step in ML model design
2. EDA can lead us to take proper assumption while performing feature engineering and selection
3. Normalization of feature is the best practice to perform to avoid biasing while model training
4. For imbalanced dataset, it is must to perform sampling of data, otherwise the model won't be reliable
