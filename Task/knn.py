# This file is to combine data from 63 stns and their correspond locations
# and fit them into a model based on random forest regressor
import numpy as np
import datetime
from sklearn import metrics
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split 
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import KFold
from sklearn.metrics import make_scorer
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import ShuffleSplit
from sklearn.metrics import r2_score

print("The program running now is a model based on KNN regressor.")
file_path = "/Users/ue/Downloads/MachineLearning2018ESTaR/Dataset/tslist"
FinalDataset = np.zeros(shape=(2172480, 8), dtype=float)
location_nparray = np.zeros(shape=(63, 3), dtype=float)
def ReadList(file_pathway):
    f = open(file_pathway)
    line_number = 1
    i = 0
    for data in f.readlines():
        if line_number == 1 or line_number == 2 or line_number == 3:
            line_number+=1
        else:
            # remove the \n and space between data
            data = data.strip('\n')
            nums = data.split(' ')
            while '' in nums:
                nums.remove('')
            string = nums[1]
            index = string[3:]
            location_nparray[i,0] = index
            location_nparray[i,1], location_nparray[i,2] = nums[2], nums[3]
            i += 1
            if i == 63:
                break
    f.close()
ReadList(file_path)

# Read the data
def ReadFile(file_pathway):
    f = open(file_pathway)
    first_else = True
    line_number = 1
    for data in f.readlines():
        if line_number==1:
            line_number+=1
        else:
            # remove the \n and space between data
            data = data.strip('\n')
            nums = data.split(' ')
            if first_else:
                nums = [float(x) for x in nums]
                matrix = np.array(nums)
                first_else = False
            else:
                nums = [float(x) for x in nums]
                matrix = np.c_[matrix, nums]
    matrix = matrix.transpose()
    f.close()
    return matrix

dt = datetime.datetime(2015, 1, 1, 8, 0, 0)
end = datetime.datetime(2016, 1, 1, 7, 59, 59)
step = datetime.timedelta(minutes=15)
result1 = []
result2 = []
while dt < end:
    result1.append(float(dt.strftime('%Y%m%d%H%M%S')))
    result2.append(float(dt.strftime('%m')))
    dt += step
Time_long = np.asarray(result1)
month_index = np.asarray(result2)

# mean CSR value each month
dayEachMonth = {1:"31", 2:"28", 3:"31", 4:"30", 5:"31", 6:"30", 7:"31", 8:"31", 9:"30", 10:"31", 11:"30", 12:"31"}
def TotalDayInMonth(monthIndex):
    day_number = 0
    if monthIndex == 0:
        return day_number
    while monthIndex != 1:
        day_number += int(dayEachMonth[monthIndex])
        monthIndex -= 1
    
    day_number += int(dayEachMonth[1])
    return day_number

for k in range(62):
    index = k + 1
    file_path =  "/Users/ue/Downloads/MachineLearning2018ESTaR/Dataset/wrfdata." + str(index)
    location = location_nparray[index]
    startindex, endindex = 35040 * k, 35040 * (k+1)
    FinalDataset[startindex:endindex, :3] = location

    RoughDataset = np.asarray(ReadFile(file_path))
    SWDIR = RoughDataset[:, 1]
    SWDIF = RoughDataset[:, 2]
    GLW = RoughDataset[:, 3]

    CSR = SWDIF / (SWDIF + SWDIR)
    dataSize = np.size(Time_long, 0)

    ProcessedDataset = np.vstack((Time_long, month_index, CSR))
    ProcessedDataset = ProcessedDataset.transpose()

    zeroVector = np.zeros(shape=(1, dataSize))
    # 3 for day average value, 4 for month average value, 5 for CSR grouping
    ProcessedDataset = np.insert(ProcessedDataset, 3, values=zeroVector, axis=1)
    ProcessedDataset = np.insert(ProcessedDataset, 4, values=zeroVector, axis=1)
    ProcessedDataset = np.insert(ProcessedDataset, 5, values=zeroVector, axis=1)
    # below is to convert ratio CSR to correspond group 0-10
    for element in ProcessedDataset:
        if np.isnan(element[2]):
            element[5] = 0
        if element[2] < 0.1:
            element[5] = 1
        elif element[2] < 0.2:
            element[5] = 2
        elif element[2] < 0.3:
            element[5] = 3
        elif element[2] < 0.4:
            element[5] = 4
        elif element[2] < 0.5:
            element[5] = 5
        elif element[2] < 0.6:
            element[5] = 6
        elif element[2] < 0.7:
            element[5] = 7
        elif element[2] < 0.8:
            element[5] = 8
        elif element[2] < 0.9:
            element[5] = 9
        else:
            element[5] = 10
    # mean CSR value each day
    for j in range(365):
        indexa, indexb = j * 365, (j+1) * 365
        ProcessedDataset[indexa:indexb, 3] = np.mean(ProcessedDataset[indexa:indexb, 5])
    # mean CSR value each month
    for i in range(12):
        MonthIndex = i + 1
        DayNumber1, DayNumber2 = 0, 0
        DayNumber1 = TotalDayInMonth(i)
        DayNumber2 = TotalDayInMonth(MonthIndex)
        if i == 11:
            ProcessedDataset[DayNumber1:DayNumber2, 4] = np.mean(ProcessedDataset[DayNumber1:, 5])
            break
        ProcessedDataset[DayNumber1:DayNumber2, 4] = np.mean(ProcessedDataset[DayNumber1:DayNumber2, 5])
    # ProcessedDataset should contain 5 columns:
    # time long float, month index, day mean CSR, month mean CSR, actual CSR group
    ProcessedDataset = np.delete(ProcessedDataset, 2, 1)
    # print("Shape of ProcessedDataset: ", ProcessedDataset.shape)
    # print("Shape of fit in final dataset: ", FinalDataset[startindex:endindex, 3:8].shape)
    FinalDataset[startindex:endindex, 3:8] = ProcessedDataset
    print("Current range index k is: ", k)

print("Great to know you have completed the read in of dataset!!!")
print("Now is the more time consuming part..")
np.random.shuffle(FinalDataset)
SampleSet = FinalDataset[:, :]
print("Shape of final dataset: ", FinalDataset.shape)
X_sample, y_sample = SampleSet[:, :7], SampleSet[:, 7]
x_train, x_test, y_train, y_test = train_test_split(X_sample, y_sample, test_size=0.1, random_state=42)

print("Now begin to fit in the data.")
start_time = datetime.datetime.now()

# def performance_metric(y_true,y_pred):
#     score=r2_score(y_true,y_pred)
#     return score
# def fit_model_shuffle(X,y):
#     cv_sets = ShuffleSplit(n_splits = 10, test_size = 0.20, random_state = 0)
#     knn = KNeighborsRegressor()
#     params={'n_neighbors':range(3,10)}
#     scoring_fnc=make_scorer(performance_metric)
#     grid=GridSearchCV(knn, param_grid=params,scoring=scoring_fnc,cv=cv_sets)
#     grid = grid.fit(X, y)
#     return grid.best_estimator_
# def fit_model_k_fold(X,y):
#     k_fold=KFold(n_splits=5)
#     knn=KNeighborsRegressor()
#     params={'n_neighbors':range(100,1000,10), 'n_jobs':[-1]}
#     scoring_fnc=make_scorer(performance_metric)
#     grid = GridSearchCV(knn, param_grid=params,scoring=scoring_fnc,cv=k_fold)
#     grid = grid.fit(X, y)
#     return grid.best_estimator_
# # reg = fit_model_k_fold(x_train, y_train)
# # print(reg.get_params())

reg = KNeighborsRegressor(n_neighbors=400)
reg.fit(x_train, y_train)

print("Data fit in successfully!")

end_time = datetime.datetime.now()
print("Time taken to run the program till fit in of all the data: ", (end_time-start_time).seconds, " seconds")

start_time = datetime.datetime.now()
print("The score for KNN regressor.")

# def mean_absolute_percentage_error(y_true, y_pred): 
#     y_true, y_pred = np.array(y_true), np.array(y_pred)
#     return np.mean(np.abs((y_true - y_pred) / y_true)) * 1

y_train_pre = reg.predict(x_train)
print("train: MAE: ", metrics.mean_absolute_error(y_train, y_train_pre))
print("train: MSE: ",  metrics.mean_squared_error(y_train, y_train_pre))
print("train: RMSE: ", np.sqrt(metrics.mean_squared_error(y_train, y_train_pre)))
# print("train: MAPE: ", mean_absolute_percentage_error(y_train, y_train_pre))

y_test_pre = reg.predict(x_test)
print("test: MAE: ", metrics.mean_absolute_error(y_test, y_test_pre))
print("test: MSE: ", metrics.mean_squared_error(y_test, y_test_pre))
print("test: RMSE: ", np.sqrt(metrics.mean_squared_error(y_test, y_test_pre)))
# print("test: MAPE: ", mean_absolute_percentage_error(y_test, y_test_pre))
end_time = datetime.datetime.now()
print("Time taken to run the program till complete the prediction and give the score: ", (end_time-start_time).seconds, " seconds")

# The score is similarly not satisfying, will try some more.
# rain: MAE:  0.9334918388201503
# train: MSE:  3.241064795088256
# train: RMSE:  1.8002957521163727
# train: MAPE: 34.526255609
# test: MAE:  0.9284054628811319
# test: MSE:  3.2160180687338733
# test: RMSE:  1.7933259794956056
# test: MAPE: 34.106331429

# sampling
# train: MAE: 1.48058
# train: MSE: 4.68965
# train: RMSE: 2.165633
# test: MAE: 1.48900
# test: MSE: 4.74354
# test: RMSE: 2.17796