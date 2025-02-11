import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import scipy.optimize as optimize
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(n_samples=100):
    """Loads sample data (replace with your actual data)."""
    np.random.seed(0)  # for reproducibility
    altitude = np.random.uniform(0, 10000, n_samples)  # Example altitude range
    speed = np.random.uniform(200, 800, n_samples)    # Example speed range
    lift_coeff = 0.2 + 0.0001 * speed + 0.000001 * speed**2 + 0.00005 * altitude + np.random.normal(0, 0.02, n_samples) # Example lift equation (with noise)
    drag_coeff = 0.01 + 0.00002 * speed + 0.0000005 * speed**2 + 0.00001 * altitude + np.random.normal(0, 0.01, n_samples) # Example drag equation (with noise)
    data = pd.DataFrame({'altitude': altitude, 'speed': speed, 'lift_coeff': lift_coeff, 'drag_coeff': drag_coeff})
    return data

def correlation_analysis(data):
    """Performs correlation analysis."""
    correlation_matrix = data.corr()
    print("Correlation Matrix:\n", correlation_matrix)
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
    plt.title('Correlation Heatmap')
    plt.show() # Display the heatmap
    return correlation_matrix

def regression_analysis(data, degree=2):
    """Performs polynomial regression."""
    X = data[['altitude', 'speed']]
    y_lift = data['lift_coeff']
    y_drag = data['drag_coeff']

    poly = PolynomialFeatures(degree=degree, include_bias=False)
    X_poly = poly.fit_transform(X)

    model_lift = LinearRegression()
    model_lift.fit(X_poly, y_lift)

    model_drag = LinearRegression()
    model_drag.fit(X_poly, y_drag)

    return model_lift, model_drag, poly

def range_reduction_optimization(model_lift, poly, target_lift, bounds, initial_guess):
    """Performs range reduction using optimization."""

    def lift_objective_function(variables):
        altitude, speed = variables
        X_test = np.array([[altitude, speed]])
        X_test_poly = poly.transform(X_test)
        predicted_lift = model_lift.predict(X_test_poly)[0]
        return (predicted_lift - target_lift)**2

    result = optimize.minimize(lift_objective_function, initial_guess, bounds=bounds)

    if result.success:
        optimal_altitude, optimal_speed = result.x
        print(f"Optimal Altitude (for target lift {target_lift}): {optimal_altitude:.2f}")
        print(f"Optimal Speed (for target lift {target_lift}): {optimal_speed:.2f}")
        return optimal_altitude, optimal_speed
    else:
        print("Optimization failed.")
        return None, None

def range_reduction_percentile(data, target_drag_percentile):
    """Performs range reduction using percentile analysis."""
    target_drag = data['drag_coeff'].quantile(target_drag_percentile)

    # A more robust approach to finding speed range:
    speeds_below_target = data[data['drag_coeff'] <= target_drag]['speed']
    if not speeds_below_target.empty:
        lower_speed_bound = speeds_below_target.max()
    else:
        lower_speed_bound = data['speed'].min() # Handle cases where no speeds are below target

    upper_speed_bound = data['speed'].max()
    print(f"Speed Range for {target_drag_percentile*100:.0f}th percentile of Drag: ({lower_speed_bound:.2f}, {upper_speed_bound:.2f})")
    return lower_speed_bound, upper_speed_bound


def predict_performance(model_lift, model_drag, poly, altitude, speed):
    """Predicts performance using the trained models."""
    X_test = np.array([[altitude, speed]])
    X_test_poly = poly.transform(X_test)

    predicted_lift = model_lift.predict(X_test_poly)[0]
    predicted_drag = model_drag.predict(X_test_poly)[0]

    return predicted_lift, predicted_drag

def drag_objective_function(variables, model_drag, poly, target_drag):
    """Objective function for drag coefficient optimization."""
    altitude, speed = variables
    X_test = np.array([[altitude, speed]])
    X_test_poly = poly.transform(X_test)
    predicted_drag = model_drag.predict(X_test_poly)[0]
    return (predicted_drag - target_drag)**2

def normal_force_objective_function(variables, model_normal, poly, target_normal):
    """Objective function for normal force coefficient optimization."""
    altitude, speed = variables
    X_test = np.array([[altitude, speed]])
    X_test_poly = poly.transform(X_test)
    predicted_normal = model_normal.predict(X_test_poly)[0]
    return (predicted_normal - target_normal)**2


def range_reduction_optimization_drag(model_drag, poly, target_drag, bounds, initial_guess):
    """Performs range reduction for drag using optimization."""
    result = optimize.minimize(drag_objective_function, initial_guess, args=(model_drag, poly, target_drag), bounds=bounds)

    if result.success:
        optimal_altitude, optimal_speed = result.x
        print(f"Optimal Altitude (for target drag {target_drag}): {optimal_altitude:.2f}")
        print(f"Optimal Speed (for target drag {target_drag}): {optimal_speed:.2f}")
        return optimal_altitude, optimal_speed
    else:
        print("Drag optimization failed.")
        return None, None

def range_reduction_optimization_normal(model_normal, poly, target_normal, bounds, initial_guess):
    """Performs range reduction for normal force using optimization."""

    result = optimize.minimize(normal_force_objective_function, initial_guess, args=(model_normal, poly, target_normal), bounds=bounds)

    if result.success:
        optimal_altitude, optimal_speed = result.x
        print(f"Optimal Altitude (for target normal force {target_normal}): {optimal_altitude:.2f}")
        print(f"Optimal Speed (for target normal force {target_normal}): {optimal_speed:.2f}")
        return optimal_altitude, optimal_speed
    else:
        print("Normal force optimization failed.")
        return None, None

if __name__ == "__main__":
    # Main execution
    data = load_data()

    # Step 2: Statistical Analysis
    correlation_matrix = correlation_analysis(data)

    # Step 3: Regression Analysis
    model_lift, model_drag, poly = regression_analysis(data, degree=2)  # Adjust degree as needed

    # Step 4: Range Reduction (Combined)
    bounds = [(data['altitude'].min(), data['altitude'].max()), (data['speed'].min(), data['speed'].max())]
    initial_guess = [data['altitude'].mean(), data['speed'].mean()]

    target_lift = 0.55  # Example
    optimal_altitude_lift, optimal_speed_lift = range_reduction_optimization(model_lift, poly, target_lift, bounds, initial_guess)

    target_drag_percentile = 0.25  # Example
    lower_speed_drag, upper_speed_drag = range_reduction_percentile(data, target_drag_percentile)


    # Example prediction:
    test_altitude = 6000
    test_speed = 600
    predicted_lift, predicted_drag = predict_performance(model_lift, model_drag, poly, test_altitude, test_speed)
    print(f"Predicted lift at {test_altitude} altitude and {test_speed} speed: {predicted_lift:.3f}")
    print(f"Predicted drag at {test_altitude} altitude and {test_speed} speed: {predicted_drag:.3f}")


    # Example of using the reduced ranges for your high-fidelity code:
    # You would now use the calculated optimal_altitude, optimal_speed_lift, lower_speed_drag, and upper_speed_drag
    # to define the ranges for your high-fidelity simulations.  For example:

    # altitude_range_high_fidelity = (optimal_altitude_lift * 0.9, optimal_altitude_lift * 1.1)  # Example: +/- 10%
    # speed_range_high_fidelity = (lower_speed_drag, upper_speed_drag)

    # Main execution
    data = load_data()

    # Step 2: Statistical Analysis
    correlation_matrix = correlation_analysis(data)

    # Step 3: Regression Analysis (Assuming you also have a normal force coefficient in your data)
    model_lift, model_drag, poly = regression_analysis(data, degree=2)  # Adjust degree as needed

    # Assuming you've trained a model for normal force as well:
    # model_normal = ...  (Train your normal force model here, similar to lift and drag)

    # Step 4: Range Reduction (Combined)
    bounds = [(data['altitude'].min(), data['altitude'].max()), (data['speed'].min(), data['speed'].max())]
    initial_guess = [data['altitude'].mean(), data['speed'].mean()]

    target_lift = 0.55  # Example
    optimal_altitude_lift, optimal_speed_lift = range_reduction_optimization(model_lift, poly, target_lift, bounds, initial_guess)

    target_drag = 0.05  # Example
    optimal_altitude_drag, optimal_speed_drag = range_reduction_optimization_drag(model_drag, poly, target_drag, bounds, initial_guess)

    # Example for normal force (replace with your actual target and trained model):
    # target_normal = 1.2  # Example
    # optimal_altitude_normal, optimal_speed_normal = range_reduction_optimization_normal(model_normal, poly, target_normal, bounds, initial_guess)


    target_drag_percentile = 0.25  # Example
    lower_speed_drag, upper_speed_drag = range_reduction_percentile(data, target_drag_percentile)

    