import pickle
from sklearn.linear_model import LogisticRegression
input_file = 'model_C=1.0.bin'
with open(input_file, 'rb') as f_in:
    dv, model = pickle.load(f_in)

LogisticRegression(max_iter=1000)
customer = {
    "lead_source": "paid_ads",
    "number_of_courses_viewed": 2,
    "annual_income": 79276.0
}
X = dv.transform([customer])
y_pred = model.predict_proba(X)[0, 1]
print('input:', customer)
print('output:', y_pred)