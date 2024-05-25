**Sentiment Analysis for Amharic and English texts**
-Data Preprocessing: pandas, tensorflow.keras
-Data Augmentation: nlplaug
-Feature Extraction: TfdfVectorizer
-Classifiers: SVM, Naive Bayes, and a stacked classifier (SVM, Naive Bayes, Logistic Regression, XGBoost)
Accuracy(using Stacked Classifier)
Amharic Model: 87%
English Model: 95%
**Completed APIS**
User Management
✅Register-http://localhost:8000/api/register/
✅Login- http://localhost:8000/api/login/
✅Logout-http://localhost:8000/api/logout/
✅list-allusers-http://localhost:8000/api/users/
✅update-account-http://localhost:8000/api/user/<int:id>/update/
✅delete-account-http://localhost:8000/api/user/<int:id>/delete/
✅validate-token-http://localhost:8000/api/token/validate/
✅verify-email-http://localhost:8000/api/email-verify/
✅reset-request-email-http://localhost:8000/api/request-reset-email/
✅reset-password-http://localhost:8000/api/password-reset-complete
✅Google-signup-  http://localhost:8000/social_auth/google/
✅facebook-signup-http://localhost:8000/social_auth/facebook/
Employer service
✅post-job-http://localhost:8001
✅view-freelancers-http://localhost:8001
✅chat-http://localhost:8001
✅view-progress-http://localhost:8001

Freelancer service
✅view-job-http://localhost:8002
✅list-all-jobs-http://localhost:8002
✅apply-for-job- http://localhost:8002/api/apply
✅accept/decline application-http://localhost:8002/api/applications/1
notify-http://localhost:8002
✅submit-task-http://localhost:8002
✅view-progress-http://localhost:8002
✅chat-http://localhost:8002
Sentiment service
✅predict-sentiment-english-http://localhost:8003
✅predict-sentiment-amharic-http://localhost:8003/api/analyze-sentiment/
Payment service
pay-freelancer- -http://localhost:8004
