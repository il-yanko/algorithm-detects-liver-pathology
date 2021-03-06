#!/usr/bin/env python

import numpy as np
import pandas as pd
import pickle
#from math import ceil
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="white")
sns.set(style="whitegrid", color_codes=True)

from sklearn.decomposition import PCA, KernelPCA, FactorAnalysis
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn import linear_model,tree
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.utils.multiclass import unique_labels
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.neural_network import MLPClassifier


#from boruta import BorutaPy

import warnings
warnings.filterwarnings("ignore")


def plot_confusion_matrix(y_true, y_pred, classes,
                          normalize=False, title=None,
                          cmap=plt.cm.get_cmap('Reds')):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if not title:
        if normalize:
            title = "NORMALIZED CONFUSION MATRIX"
        else:
            title = "NON-NORMALIZED CONFUSION MATRIX"

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    # Only use the labels that appear in the data
    #classes = classes[unique_labels(y_true, y_pred)]
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("NORMALIZED CONFUSION MATRIX")
    else:
        print("NON-NORMALIZED CONFUSION MATRIX")

    print(cm)

    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes,
           ylabel='TRUE CLASS',
           xlabel='PREDICTED CLASS'
           )
    ax.set_title(title, fontsize=22)

    # Rotate the tick labels and set their alignment.
    #plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
    #         rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center", fontsize=20,
                    color="white" if cm[i, j] > thresh else "black")
            ax.tick_params(labelsize=20)
    fig.tight_layout()
    return ax

path = "data/result/features.csv"
bestnorm = [
            "original_glrlm_RunEntropy",
            "original_glrlm_GrayLevelNonUniformity",
            "original_firstorder_10Percentile",
            #"original_gldm_GrayLevelNonUniformity",
            #"diagnostics_Image-original_Mean"
           ]
bestwls = [
            'original_glrlm_RunEntropy',
            #'original_glrlm_RunLengthNonUniformity',
            #"diagnostics_Image-original_Mean",
            "original_firstorder_90Percentile",
          ]
besthpc = [
            #"diagnostics_Image-original_Mean",
            #"diagnostics_Image-original_Minimum",
            #"diagnostics_Image-original_Maximum",
            #"original_firstorder_10Percentile",
            #"original_firstorder_90Percentile",
            #"original_gldm_GrayLevelNonUniformity",
            "original_glcm_ClusterShade",
            "original_firstorder_RobustMeanAbsoluteDeviation",
            #"original_firstorder_TotalEnergy",
            "original_glrlm_RunEntropy",
            #"original_gldm_DependenceNonUniformity",
            #"original_glrlm_LongRunHighGrayLevelEmphasis",
            "original_gldm_LargeDependenceEmphasis"
          ]
besthpb = [
            "original_gldm_DependenceVariance",
            #"diagnostics_Image-original_Mean",
            "original_glcm_ClusterShade",
            #"original_gldm_LargeDependenceLowGrayLevelEmphasis",
            "original_glcm_Idmn",
            "original_firstorder_Skewness",
            "original_ngtdm_Strength",
            #"original_gldm_DependenceNonUniformity",
            #"original_firstorder_Kurtosis",
            #"original_firstorder_Energy",
            #"original_glrlm_GrayLevelNonUniformity",
]
bestauh = [
            'original_firstorder_TotalEnergy',
            'original_firstorder_Energy',
            'original_glcm_ClusterProminence',
            'original_glcm_Imc1'
          ]

data = pd.read_csv(path, ";")

# radviz (Dimensional Anchor)
'''
# крутая штука показывает важность многих фич на 2д картинке
choice = bestnorm
choice.append('isnorm')
from pandas.plotting import radviz
plt.figure()
radviz(data[choice], 'isnorm', color=['blue','red'])
plt.show()
'''

# seaborn
'''
red_blue = ["#ff0000", "#1240ab"]
sns.pairplot(
    data,
    vars=besthpb,
    hue='ishpb',
    aspect=0.3,
    palette=red_blue,
    #kind="skatter"
    #markers="."
)
plt.show()
plt.tight_layout()
'''

#====================================================================
# download train and test data
test_path = "data/result/test.csv"
test = pd.read_csv(test_path, ";")
train_path = "data/result/train.csv"
train = pd.read_csv(train_path, ";")

all = ["norm", "auh", "hpb", "hpc", "wls"]
wls = ['notwls','wls']
hpb = ['notHPB','HPB']
hpc = ['notHPC','HPC']
auh = ['notAuh','auh']
norma = ['patho','norma']
cf = ['notCf', 'Cf']

cols_to_drop = ['id','data_source','diagnosis_code','isnorm','isauh','ishpb','ishpc','iswls']
model_features = [col for col in train.columns if col not in cols_to_drop]

# pool of all classification settings
poolParam = ["diagnosis_code","iswls","ishpb","ishpc","isauh","isnorm","iscf"]
poolLabel = [all, wls, hpb, hpc, auh, norma, cf]


poolTests = {poolParam[a]:poolLabel[a] for a in range (len(poolParam))}

# single classification setting
#model_parameter = "diagnosis_code"
#model_labels = all

#====================================================================

def predict_and_show(X_train, y_train, X_test, y_test, clf, plt, names, clf_name, param):
    print("\n", clf_name, ":\n================================================\nPredictable attribute: ", param)
    cur = clf.fit(X_train, y_train)
    # Test the classifier
    y_pred = cur.predict(X_test)
    print("Accuracy:%.2f%%" % (float(accuracy_score(y_test, y_pred)) * 100))
    print("Prediction:\n", y_pred)
    print("Real test:\n", y_test.to_numpy())
    # print(classification_report(y_test, y_pred, target_names=names))
    # Plot normalized confusion matrix
    # if you need numbers: classes=np.asarray(unique_labels(y_test), dtype=int)
    plot_confusion_matrix(y_test, y_pred, classes=names, normalize=True, title=clf_name)
    plt.show()

clf_names,clf_models  = list(), list()


'''
clf_models.append(make_pipeline (#PCA(n_components=2),
                                 StandardScaler(),
                                 tree.DecisionTreeClassifier(random_state=0,criterion='gini',max_features=2)))
clf_names.append("Decision Tree Classifier")

clf_models.append(make_pipeline (StandardScaler(),KernelPCA(n_components=24,kernel='rbf'),#,FactorAnalysis(n_components=29)
                                 MLPClassifier(solver='lbfgs', alpha=1e-3, shuffle=True,
                                               activation='logistic', max_iter=1000000,
                                               hidden_layer_sizes=(5, 13), random_state=1),
                                 ))
clf_names.append("Multi-layer Perceptron")

clf_models.append(make_pipeline (PCA(n_components=2),
                                 StandardScaler(),
                                 linear_model.SGDClassifier(max_iter=1000000, tol=1e-3),
                                 ))
clf_names.append("Stochastic Gradient Descent")

clf_models.append(make_pipeline (PCA(n_components=3), StandardScaler(),
                                 linear_model.LogisticRegression(max_iter=1000000, C=1e3,
                                                     solver='newton-cg',penalty="l2" ,multi_class='multinomial'
                                                                 )))
clf_names.append("Logistic Regression")

clf_models.append(make_pipeline (PCA(n_components=5), StandardScaler(),
                                 RandomForestClassifier(max_depth=10, n_estimators=100,
                                            max_features=2, random_state=0, #class_weight='balanced',
                                            criterion='gini',bootstrap=False)))
clf_names.append("Random Forest Classifier")

clf_models.append(make_pipeline (PCA(n_components=3), #StandardScaler(),
                                 svm.SVC(gamma='scale', kernel='rbf')))
clf_names.append("C-Support Vector Machine")

clf_models.append(make_pipeline (StandardScaler(), KernelPCA(n_components=10,kernel='rbf'),
                                 GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=10,
                                                            random_state=0, loss='deviance')
                                 )
                  )
clf_names.append("Gradient Boosting")

'''

clf_models.append(make_pipeline (StandardScaler(), KernelPCA(n_components=24,kernel='rbf'),
                                 KNeighborsClassifier(5, algorithm='auto', metric='manhattan')
                                 )
                  )
clf_names.append("k-Nearest Neighbors")



clfs = {clf_names[a]:clf_models[a] for a in range(len(clf_names))}

# Normal model estimation + test/train separated with hands
'''
for name,model in clfs.items():
    for param, label in poolTests.items():

        # X_train = train.iloc[:, 1:train.shape[1] - 7]
        X_train = train[model_features]
        y_train = train[param].astype(int)

        # X_test = test.iloc  [:, 1:train.shape[1] - 7]
        X_test = test[model_features]
        y_test = test[param].astype(int)

        predict_and_show(X_train, y_train, X_test, y_test, model, plt, label, name, param)
'''

# Cross Validation (K-fold) model estimation
def k_fold_cv(data, model_features, clf, clf_name, criterion, cv_number=10):
    X = data[model_features]
    y = data[criterion].astype(int)

    print("================================================\n{}:\nPredictable "
          "attribute: {}\n".format(clf_name, criterion))
    # cross_val = KFold(n_splits=5, shuffle=True, random_state=1)
    # for train, test in cross_val.split(data):
    #    print('train: %s, test: %s' % (train, test))

    rez = np.mean(cross_val_score(clf, X, y, cv=cv_number, scoring='accuracy'))
    rez = int(round( float(rez), 2) * 100)
    print('Accuracy = {}%'.format(rez))
    return rez


# pool of all classification settings
poolParam = ["diagnosis_code"]#,"iswls","ishpb","ishpc","isauh","isnorm","iscf"]
poolLabel = [all]#, wls, hpb, hpc, auh, norma, cf]
poolTests = {poolParam[a]:poolLabel[a] for a in range (len(poolParam))}


#K-fold
'''
for name,model in clfs.items():
    for param, label in poolTests.items():
        k_fold_cv(data, model_features, model, name, param, cv_number=10)
'''

# відбір моделі !!!!!!!!!!

for param, label in poolTests.items():
    # Options for model size

    #n_layers = np.arange(2, int(20), 1)
    n_layers = list([1])
    m_components = np.arange(2, int(30), 1)
    super_scores = dict()

    for layer in n_layers:
        scores = list()
        for component in m_components:
            model_name = "Multi-layer Perceptron"
            model_name = "{} ({} layers, {} components)".format(model_name, layer, component)
            model = make_pipeline (StandardScaler(), #PCA(n_components=component),
                                   KernelPCA(n_components=component,kernel='rbf'),
                                   #FactorAnalysis(n_components=model_size),
                                   #KernelPCA(n_components=model_size,kernel='sigmoid'),
                                   #LDA(n_components=model_size,solver='svd'),
                                   #RandomForestClassifier(max_depth=100, n_estimators=100,
                                   #                       max_features=int(2), random_state=0,
                                   #                       #class_weight='balanced',
                                   #                       criterion='gini', bootstrap=True)
                                   #svm.SVC(max_iter=-1, gamma='scale', kernel='rbf')
                                   #GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=10,
                                   #                            random_state=0,loss='deviance', max_features=component)
                                   #KNeighborsClassifier(5, algorithm='auto', metric='manhattan')
                                   linear_model.LogisticRegression(max_iter=1000000, C=1e3, penalty="l2",
                                                                  solver='newton-cg', multi_class='multinomial')
                                   #MLPClassifier(solver='lbfgs', alpha=1e-3, shuffle=True,
                                   #               activation='logistic', max_iter=1000000,
                                   #               hidden_layer_sizes=(5, layer), random_state=0),
                                   )
            scores.append(k_fold_cv(data, model_features, model, model_name, param, cv_number=5))
        print(scores,'\n')
        best = max(scores)
        best_component = m_components[np.argmax(scores)]
        super_scores[best] = 'Logistic Regression({}) + KPCA-RBF({})'.format(layer, int(best_component))
        #print("Кращий результат {}-шаровго MLP - {}%\n дає модель зі {} компонент".format(layer, best,best_component))
        print("Кращий результат LR - {}%\n дає модель зі {} компонент".format(best, best_component))
        plt.figure()
        plt.plot(m_components, scores, label='ТОЧНІСТЬ класифікації', lw=5, color='r')
        #plt.axhline(y=50, lw=3, color='k', linestyle='--', label='50% шанс')
        plt.axhline(y=best, lw=3, color='k', linestyle='--', label=str(best)+'%')
        plt.axvline(x=best_component, lw=1, color='k', linestyle='-')
        plt.xlabel('Кількість компонент ЯМГК (РБФ)')
        plt.ylabel('Точність')
        plt.ylim(50,100)
        plt.legend(loc='lower right')
        #plt.title("Багатошаровий перцептрон ({} шарів) + ЯМГК (РБФ)".format(layer))
        plt.title("Логістична Регресія + ЯМГК (РБФ)")
        #plt.show()
        #plt.savefig('data/result/experiments/MLP({})_KPCA_RBF({}).png'.format(int(layer),int(best_component)),bbox_inches='tight')
        plt.savefig('data/result/experiments/LR_KPCA_RBF({}).png'.format(int(best_component)), bbox_inches='tight')

    super_best = max(super_scores, key=int)
    print("СУПЕР-кращий результат - {} = {}".format(super_best,super_scores[super_best]))




# RFECV
'''
# Recursive feature elimination with cross-validation
def compute_RFECV (data, model_features, clf, clf_name, criterion, cv_number=5):

    from sklearn.model_selection import StratifiedKFold
    from sklearn.feature_selection import RFECV

    X = data[model_features]
    y = data[criterion]

    print("================================================\n{}:\nPredictable "
          "attribute: {}\n".format(clf_name, criterion))
    # cross_val = KFold(n_splits=5, shuffle=True, random_state=1)
    # for train, test in cross_val.split(data):
    #    print('train: %s, test: %s' % (train, test))

    rfecv = RFECV(estimator=clf, step=1, cv=cv_number, scoring='accuracy')
    rfecv.fit(X, y)

    print("Optimal number of features : %d" % rfecv.n_features_)

    # Plot number of features VS. cross-validation scores
    plt.figure()
    plt.xlabel("Number of features selected")
    plt.ylabel("Cross validation score (nb of correct classifications)")
    plt.plot(range(1, len(rfecv.grid_scores_) + 1), rfecv.grid_scores_)
    plt.show()

from sklearn.pipeline import Pipeline

class PipelineRFE(Pipeline):
    def fit(self, X, y=None, **fit_params):
        super(PipelineRFE, self).fit(X, y, **fit_params)
        self.feature_importances_ = self.steps[-1][-1].feature_importances_
        return self

for param, label in poolTests.items():
    from sklearn.ensemble import ExtraTreesClassifier
    #from sklearn.svm import LinearSVC
    model_name = "SVR"
    model = PipelineRFE(
        [
            ('std_scaler', StandardScaler()),
            # RandomForestClassifier(max_depth=100, n_estimators=100,
            #                       max_features=int(2), random_state=0,
            #                       #class_weight='balanced',
            #                       criterion='gini', bootstrap=True)
            ("ET", ExtraTreesClassifier(random_state=0, n_estimators=1000))
            #('SVR',LinearSVC(random_state=0, tol=1e-5))#max_iter=-1, gamma='scale', kernel='linear'))
            # GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=10,
            #                            random_state=0,loss='deviance', max_features=component)
            #('LR',linear_model.LogisticRegression(max_iter=1000000, C=1e3, penalty="l2",
            #                                solver='newton-cg', multi_class='multinomial'))
        ]
    )
    compute_RFECV(data, model_features, model, model_name, param, cv_number=5)
'''


# REDO !!!!!!!!!!!!!!!!!!!!
def roc ():
    from sklearn.metrics import roc_curve, auc
    for name,model in clfs.items():
        for param, label in poolTests.items():

            from sklearn.multiclass import OneVsRestClassifier
            from sklearn.preprocessing import label_binarize
            from scipy import interp
            from itertools import cycle

            model = OneVsRestClassifier(model)

            X_train = train[model_features]
            y_train = label_binarize(train[param].astype(int).as_matrix(),classes=[0, 1, 2,3,4])
            X_test = test[model_features]
            y_test = label_binarize(test[param].astype(int).as_matrix(),classes=[0, 1, 2,3,4])

            cur = model.fit(X_train, y_train)
            # Test the classifier
            y_score = cur.predict(X_test)

            # Compute ROC curve and ROC area for each class
            fpr = dict()
            tpr = dict()
            roc_auc = dict()

            n_classes = 5
            lw = 2
            '''
            print("test= {}".format(y_test))
            print("score= {}".format(y_score))
            '''
            for i in range(n_classes):
                fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
                roc_auc[i] = auc(fpr[i], tpr[i])

            # Compute micro-average ROC curve and ROC area
            fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_score.ravel())
            roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

            # Compute macro-average ROC curve and ROC area

            # First aggregate all false positive rates
            all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_classes)]))

            # Then interpolate all ROC curves at this points
            mean_tpr = np.zeros_like(all_fpr)
            for i in range(n_classes):
                mean_tpr += interp(all_fpr, fpr[i], tpr[i])

            # Finally average it and compute AUC
            mean_tpr /= n_classes

            fpr["macro"] = all_fpr
            tpr["macro"] = mean_tpr
            roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

            # Plot all ROC curves
            plt.figure()
            plt.plot(fpr["micro"], tpr["micro"],
                     label='мікро-усереднена ROC крива (площа = {0:0.2f})'
                           ''.format(roc_auc["micro"]),
                     color='deeppink', linestyle=':', linewidth=5)

            plt.plot(fpr["macro"], tpr["macro"],
                     label='макро-усереднена ROC крива (площа = {0:0.2f})'
                           ''.format(roc_auc["macro"]),
                     color='navy', linestyle=':', linewidth=5)

            label_ukr = ["норма", "аутоімунний гепатит", "гепатит В", "гепатит С", "хвороба Вільсона"]

            colors = cycle(['#FF0000', '#1B1BB3', '#269926', '#C30083', '#FFD300'])
            for i, color in zip(range(n_classes), colors):
                plt.plot(fpr[i], tpr[i], color=color, lw=lw, linewidth=3,linestyle='-',
                         label='ROC крива класу {0} (площа = {1:0.2f})'
                               ''.format(label_ukr[i], roc_auc[i]))

            plt.plot([0, 1], [0, 1], 'k--', lw=lw, linewidth=3)
            plt.xlim([-0.01, 1.0])
            plt.ylim([-0.01, 1.05])
            plt.xlabel('Частка ХИБНО ПОЗИТИВНИХ')
            plt.ylabel('Частка ІСТИНО ПОЗИТИВНИХ')
            plt.title('ROC обраної моделі')
            plt.legend(loc="lower right")
            plt.show()
# ROC (only for diagnosis_code!)
#roc()


# ROC analysis and Cross-Validation
def roc_cv (data, model_features, criterion, criterion_name, clf, clf_name, cv_number=5):

    X = data[model_features].as_matrix()
    y = data[criterion].as_matrix().astype(int)

    from scipy import interp
    from sklearn.metrics import roc_curve, auc
    from sklearn.model_selection import StratifiedKFold

    # Classification and ROC analysis

    # Run classifier with cross-validation and plot ROC curves
    cv = StratifiedKFold(n_splits=cv_number)

    tprs = []
    aucs = []
    mean_fpr = np.linspace(0, 1, 100)

    i = 0
    for train, test in cv.split(X, y):
        probas_ = clf.fit(X[train], y[train]).predict_proba(X[test])
        # Compute ROC curve and area the curve
        fpr, tpr, thresholds = roc_curve(y[test], probas_[:, 1])
        tprs.append(interp(mean_fpr, fpr, tpr))
        tprs[-1][0] = 0.0
        roc_auc = auc(fpr, tpr)
        aucs.append(roc_auc)
        #plt.plot(fpr, tpr, lw=2, alpha=0.8, label='ROC fold %d (площа = %0.2f)' % (i+1, roc_auc))
        i += 1
    plt.plot([0, 1], [0, 1], linestyle='--', lw=2, color='k', alpha=.8)

    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    std_auc = np.std(aucs)
    plt.plot(mean_fpr, mean_tpr, color='r',linewidth=5,
             label=r'Середня ROC (площа = %0.2f $\pm$ %0.2f)' % (mean_auc, std_auc),
             lw=2, alpha=.8)

    std_tpr = np.std(tprs, axis=0)
    tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
    tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
    plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2,
                     label=r'$\pm$ 1 сер. квадр. відх.')

    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('Частка ХИБНО ПОЗИТИВНИХ')
    plt.ylabel('Частка ІСТИНО ПОЗИТИВНИХ')
    plt.title('ROC моделі {} для {}'.format(criterion_name,clf_name))
    plt.legend(loc="lower right")
    plt.show()

'''
# pool of all classification settings
poolParam = ["diagnosis_code","iswls","ishpb","ishpc","isauh","isnorm","iscf"]
poolLabel = [all, wls, hpb, hpc, auh, norma, cf]
poolTests = {poolParam[a]:poolLabel[a] for a in range (len(poolParam))}
kind_ukr = ["хвороба Вільсона - проти всіх", "гепатит В - проти всіх", "гепатит С - проти всіх",
            "аутоімунний гепатит - проти всіх", "норма - патологія", "кістозний фіброз - проти всіх"]
for name,model in clfs.items():
    i = 0
    for param, label in poolTests.items():
        roc_cv(data, model_features, param, kind_ukr[i], model, name, cv_number=5)
        i = i + 1
'''



# model saving
'''
# TODO: save all model and their accuracies

for name,model in clfs.items():
    for param, label in poolTests.items():

        X1 = data[model_features]
        y1 = data[param].astype(int)

        model.fit(X1, y1)
        filename = 'data/result/model/'+ name + ' ' + param +'.sav'
        file = open(filename, 'wb')
        pickle.dump(model, file)
        print("Model called <", name, param, "> was saved")
        file.close()
'''










# Different additional unused code
'''
# Multi-Logit: choose best features and show new model
clf = make_pipeline (PCA(n_components=5),StandardScaler(),
                     linear_model.LogisticRegression(max_iter=10000, C=1e5, solver='lbfgs',multi_class='multinomial'))
print("MODEL:")
for i in range(len(model_features)):
    print(model_features[i],clf.coef_[0][i])
# calculate the features importance
coefs,arr = list(),list()
for i in range(len(clf.coef_[0])):
    a = float(np.std(X_train, 0)[i] * clf.coef_[0][i])
    b = (a, i)
    coefs.append(b)
dtype = [('coef',float), ('number',int)]
arr = np.sort(np.array(coefs, dtype=dtype), order='coef', kind='mergesort')[::-1]
# choose most important features
best = list()
modelSize = 7
for i in range (modelSize):
    best.append(X_test.columns[arr[i][1]])
# recalculate model
X_train = X_train[best]
X_test = X_test[best]
print("OPTIMIZED MODEL:\n")
print('best=',best)
clf1 = linear_model.LogisticRegression(max_iter=10000, C=1e5, solver='lbfgs')#,multi_class='multinomial')
clf1.fit(X_train, y_train)
# Test the classifier
y_pred = clf1.predict(X_test)
print("Accuracy:%.2f%%" % (float(accuracy_score(y_test, y_pred))*100))
print("Prediction:\n",y_pred)
print("Real test:\n",y_test.to_numpy())
print(classification_report(y_test, y_pred, target_names=model_names))


# XGBoost
from xgboost import XGBClassifier, plot_importance
print("\nXGBoost Classification:\n===================\nPredictable attribute: ",current)
# fit model on all training data
model = XGBClassifier()
model.fit(X_train, y_train)
plot_importance(model)
plt.show()

# make predictions for test data and evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("Accuracy: %.2f%%" % (accuracy * 100.0))
print("Prediction:\n",y_pred)
print("Real data:\n",y_test.to_numpy())

# Fit model using each importance as a threshold
thresholds = np.sort(model.feature_importances_)
#print("thresholds:", thresholds)

# XGB: cycle
for thresh in thresholds:
    # select features using threshold
    selection = SelectFromModel(model, threshold=thresh, prefit=True)
    select_X_train = selection.transform(X_train)
    # train model
    selection_model = XGBClassifier()
    selection_model.fit(select_X_train, y_train)
    # eval model
    select_X_test = selection.transform(X_test)
    y_pred = selection_model.predict(select_X_test)
    predictions = [round(value) for value in y_pred]
    accuracy = accuracy_score(y_test, predictions)
    print("Thresh=%.3f, n=%d, Accuracy: %.2f%%" % (thresh, select_X_train.shape[1], accuracy*100.0))

# XGB: hand-made threshold
# select features using threshold
threshold = 0.06
selection = SelectFromModel(model, threshold=threshold, prefit=True)
select_X_train = selection.transform(X_train)
# train model
selection_model = XGBClassifier()
selection_model.fit(select_X_train, y_train)
# eval model
select_X_test = selection.transform(X_test)
y_pred = selection_model.predict(select_X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Thresh=%.3f, n=%d, Accuracy: %.2f%%" % (threshold, select_X_train.shape[1], accuracy*100.0))

print("Prediction:\n",y_pred)
print("Real data:\n",y_test.to_numpy())
'''

# Build correlation between all model features
'''
data = pd.read_csv(path, ";")
X_all = data[model_features]
# Draw the full plot
sns.clustermap(X_all.corr(), center=0, cmap="vlag",
               linewidths=.75, figsize=(13, 13))
plt.show()
'''
