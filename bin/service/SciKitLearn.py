from pandas import DataFrame
from sklearn import linear_model, gaussian_process, tree, naive_bayes, neural_network
from bin.service import Cache
from bin.service import Environment
from matplotlib import pyplot
import numpy


class SciKitLearn:
    """Sci Kit Learn ML Stack"""

    def __init__(self):
        self.cache = Cache.Cache()
        self.environment = Environment.Environment()

    def estimate(self, target_data, source_data, target_attribute, source_attributes):

        x, y = self.frame_data(source_data, target_attribute, source_attributes)
        models = self.shotgun_models(x, y)
        model = self.get_highest_scoring_model(models, x, y)
        target_x, target_y = self.frame_data([target_data], target_attribute, source_attributes)
        estimations = model.predict(target_x)
        if estimations is not None and len(estimations) > 0:
            estimation = estimations[0]
        else:
            estimation = None

        self.generate_plot(model, estimations, source_attributes, target_attribute, x, y)

        return estimation

    def generate_plot(self, model, estimations, source_attributes, target_attribute, x, y):

        shape = numpy.pi * 3
        colors = ['red', 'green', 'blue', 'cyan', 'magenta', 'yellow']
        plot_path = self.environment.get_path_plot()
        pyplot.figure(num=1, figsize=(12, 8), dpi=96)
        pyplot.title(model.__class__.__name__)
        pyplot.xlim(-10, 110)
        pyplot.ylim(-10, 110)
        x_label = "% of ... estimation (black) | "
        time_percentages = round(y/y.max()*100)
        df_estimations = DataFrame(estimations)
        estimation_percentages = round(df_estimations/y.max()*100)
        for attribute in source_attributes:
            color = colors.pop()
            attribute_percentages = round(x[attribute]/x[attribute].max()*100)
            pyplot.scatter(attribute_percentages, time_percentages, s=shape, c=color, alpha=0.5)
            x_label += "{} ({}) | ".format(attribute, color)
        pyplot.hlines(y=estimation_percentages, xmin=0, xmax=100)
        pyplot.xlabel(x_label)
        pyplot.ylabel("% of {}".format(target_attribute))
        pyplot.savefig(fname=plot_path)

    @staticmethod
    def get_highest_scoring_model(models, x, y):

        highest_score = 0
        highest_scoring_model = None
        for model in models:
            score = model.score(x, y)
            if score > highest_score:
                highest_score = score
                highest_scoring_model = model

        return highest_scoring_model

    @staticmethod
    def shotgun_models(x, y):

        kernel = gaussian_process.kernels.DotProduct() + gaussian_process.kernels.WhiteKernel()
        models = [
            gaussian_process.GaussianProcessRegressor(kernel=kernel, random_state=1337).fit(x, y),
            linear_model.LinearRegression(n_jobs=2).fit(x, y),
            tree.DecisionTreeClassifier().fit(x, y),
            tree.DecisionTreeRegressor().fit(x, y),
            tree.ExtraTreeRegressor().fit(x, y),
            naive_bayes.GaussianNB().fit(x, y),
            neural_network.MLPRegressor(
                hidden_layer_sizes=(10,), activation='relu', solver='adam', alpha=0.001, batch_size='auto',
                learning_rate='constant', learning_rate_init=0.01, power_t=0.5, max_iter=1000, shuffle=True,
                random_state=9, tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True,
                early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08
            ).fit(x, y),
            linear_model.Lasso(alpha=0.1, copy_X=True, fit_intercept=True, max_iter=1000,
                               normalize=False, positive=False, precompute=False, random_state=None,
                               selection='cyclic', tol=0.0001, warm_start=False).fit(x, y)
        ]

        return models

    @staticmethod
    def frame_data(data, target_attribute, source_attributes):

        df_source_attributes = [target_attribute]
        df_source_attributes += source_attributes
        df = DataFrame(data, columns=df_source_attributes)
        df.sort_values(by=df_source_attributes)
        x = df[source_attributes].astype(int)
        y = df[target_attribute].astype(int)

        return x, y
