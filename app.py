from flask import Flask, render_template, request, url_for, session
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os
app = Flask(__name__)
app.secret_key = "anneke"  # Replace with your own secret key, needed for session management


def generate_data(N, mu, beta0, beta1, sigma2, S):
    # Generate data and initial plots

    # TODO 1: Generate a random dataset X of size N with values between 0 and 1
    X = np.random.rand(N)  # Replace with code to generate random values for X

    # TODO 2: Generate a random dataset Y using the specified beta0, beta1, mu, and sigma2
    # Generate the error term from a normal distribution with mean 0 and variance sigma2
    error = np.random.normal(0, np.sqrt(sigma2), N)

    # Generate Y using the specified beta0, beta1, mu, and error term
    Y = beta0 + beta1 * X + mu + error
    

    # TODO 3: Fit a linear regression model to X and Y
    X_reshaped = X.reshape(-1,1)
    model = LinearRegression()  # Initialize the LinearRegression model
    model.fit(X_reshaped, Y)  # Fit the model to X and Y
    slope = model.coef_[0]  # Extract the slope (coefficient) from the fitted model
    intercept = model.intercept_  # Extract the intercept from the fitted model

    # TODO 4: Generate a scatter plot of (X, Y) with the fitted regression line
    # Generate scatter plot of (X, Y)
    plt.scatter(X, Y, label="Data Points", color="blue")

    # Plot the regression line
    plt.plot(X, model.predict(X_reshaped), color="red", label=f"y = {slope:.2f}x + {intercept:.2f}")

    # Label axes and add title
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title(f"Regression Line: y = {slope:.2f}x + {intercept:.2f}")
    plt.legend()

    plot1_path = "static/plot1.png"
    plt.savefig(plot1_path)
    plt.close()
    # Replace with code to generate and save the scatter plot

    # TODO 5: Run S simulations to generate slopes and intercepts
    slopes = []
    intercepts = []

    for _ in range(S):
        # TODO 6: Generate simulated datasets using the same beta0 and beta1
        X_sim = np.random.rand(N)  # Replace with code to generate simulated X values
        error = np.random.normal(0, np.sqrt(sigma2), N)
        Y_sim = beta0 + beta1 * X_sim + mu + error   # Replace with code to generate simulated Y values

        # TODO 7: Fit linear regression to simulated data and store slope and intercept
        sim_model = LinearRegression()  # Replace with code to fit the model
        sim_model.fit(X_sim.reshape(-1, 1), Y_sim)
        sim_slope = sim_model.coef_[0]  # Extract slope from sim_model
        sim_intercept = sim_model.intercept_  # Extract intercept from sim_model

        slopes.append(sim_slope)
        intercepts.append(sim_intercept)

    # TODO 8: Plot histograms of slopes and intercepts
    plt.figure(figsize=(10, 5))
    plt.hist(slopes, bins=20, alpha=0.5, color="blue", label="Slopes")
    plt.hist(intercepts, bins=20, alpha=0.5, color="orange", label="Intercepts")
    plt.axvline(slope, color="blue", linestyle="--", linewidth=1, label=f"Slope: {slope:.2f}")
    plt.axvline(intercept, color="orange", linestyle="--", linewidth=1, label=f"Intercept: {intercept:.2f}")
    plt.title("Histogram of Slopes and Intercepts")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.legend()
    plot2_path = "static/plot2.png"
    plt.savefig(plot2_path)
    plt.close()
    # Replace with code to generate and save the histogram plot

    # TODO 9: Return data needed for further analysis, including slopes and intercepts
    # Calculate proportions of slopes and intercepts more extreme than observed
    slope_more_extreme = sum(s > slope for s in slopes) / S  
    intercept_extreme = sum(i < intercept for i in intercepts) / S  

    # Return data needed for further analysis
    return (
        X,
        Y,
        slope,
        intercept,
        plot1_path,
        plot2_path,
        slope_more_extreme,
        intercept_extreme,
        slopes,
        intercepts,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get user input from the form
        N = int(request.form["N"])
        mu = float(request.form["mu"])
        sigma2 = float(request.form["sigma2"])
        beta0 = float(request.form["beta0"])
        beta1 = float(request.form["beta1"])
        S = int(request.form["S"])
    
        # Generate data and initial plots
        (
            X,
            Y,
            slope,
            intercept,
            plot1,
            plot2,
            slope_extreme,
            intercept_extreme,
            slopes,
            intercepts,
        ) = generate_data(N, mu, beta0, beta1, sigma2, S)

        # Store data in session
        session["X"] = X.tolist()
        session["Y"] = Y.tolist()
        session["slope"] = slope 
        session["intercept"] = intercept 
        session["slopes"] = slopes 
        session["intercepts"] = intercepts
        session["slope_extreme"] = slope_extreme
        session["intercept_extreme"] = intercept_extreme
        session["N"] = N 
        session["mu"] = mu
        session["sigma2"] = sigma2
        session["beta0"] = beta0 
        session["beta1"] = beta1 
        session["S"] = S 


        # Return render_template with variables
        return render_template(
            "index.html",
            plot1=plot1,
            plot2=plot2,
            slope_extreme=slope_extreme,
            intercept_extreme=intercept_extreme,
            N=N,
            mu=mu,
            sigma2=sigma2,
            beta0=beta0,
            beta1=beta1,
            S=S,
        )
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    # This route handles data generation (same as above)
    return index()

from flask import session, request, jsonify
@app.route("/check_session")
def check_session():
    # Collect all relevant session keys for debugging
    session_data = {
        key: session.get(key) for key in [
            "N", "mu", "sigma2", "beta0", "beta1", "S", 
            "X", "Y", "slope", "intercept", "slopes", 
            "intercepts", "slope_extreme", "intercept_extreme"
        ]
    }
    return jsonify(session_data)

@app.route("/hypothesis_test", methods=["POST"])
def hypothesis_test():
    # Retrieve data from session
    N = int(session.get("N"))
    S = int(session.get("S"))
    slope = float(session.get("slope"))
    intercept = float(session.get("intercept"))
    slopes = session.get("slopes")
    intercepts = session.get("intercepts")
    beta0 = float(session.get("beta0"))
    beta1 = float(session.get("beta1"))


    parameter = request.form.get("parameter")
    test_type = request.form.get("test_type")

    # Use the slopes or intercepts from the simulations
    if parameter == "slope":
        simulated_stats = np.array(slopes)
        observed_stat = slope
        hypothesized_value = beta1
    else:
        simulated_stats = np.array(intercepts)
        observed_stat = intercept
        hypothesized_value = beta0

    # TODO 10: Calculate p-value based on test type
    if test_type == "!=":
        # Two-sided test (not equal to)
        diff_observed = abs(observed_stat - hypothesized_value)
        p_value = np.mean(abs(simulated_stats - hypothesized_value) >= diff_observed)
    elif test_type == ">":
        # Greater than test
        p_value = np.mean(simulated_stats >= observed_stat)
    elif test_type == "<":
        # Less than test
        p_value = np.mean(simulated_stats <= observed_stat)

    # TODO 11: If p_value is very small (e.g., <= 0.0001), set fun_message to a fun message
    fun_message = "Wow that is tiny" if p_value <= 0.0001 else "Not so tiny"

    # TODO 12: Plot histogram of simulated statistics
    plt.figure(figsize=(10, 5))
    plt.hist(simulated_stats, bins=20, alpha=0.7, color="skyblue", edgecolor="black", label="Simulated Stats")
    plt.axvline(observed_stat, color="red", linestyle="--", linewidth=2, label=f"Observed {parameter}: {observed_stat:.2f}")
    plt.axvline(hypothesized_value, color="green", linestyle="--", linewidth=2, label=f"Hypothesized {parameter}: {hypothesized_value:.2f}")
    
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.title(f"Histogram of Simulated {parameter.capitalize()} with Observed Value")
    plt.legend()
    
    plot3_path = "static/plot3.png"
    plt.savefig(plot3_path)
    plt.close()

    # Return results to template
    return render_template(
        "index.html",
        plot1="static/plot1.png",
        plot2="static/plot2.png",
        plot3=plot3_path,
        parameter=parameter,
        observed_stat=observed_stat,
        hypothesized_value=hypothesized_value,
        N=N,
        beta0=beta0,
        beta1=beta1,
        S=S,
        # TODO 13: Uncomment the following lines when implemented
        p_value=p_value,
        fun_message=fun_message,
    )

@app.route("/confidence_interval", methods=["POST"])
def confidence_interval():
    # Retrieve data from session
    N = int(session.get("N"))
    mu = float(session.get("mu"))
    sigma2 = float(session.get("sigma2"))
    beta0 = float(session.get("beta0"))
    beta1 = float(session.get("beta1"))
    S = int(session.get("S"))
    X = np.array(session.get("X"))
    Y = np.array(session.get("Y"))
    slope = float(session.get("slope"))
    intercept = float(session.get("intercept"))
    slopes = session.get("slopes")
    intercepts = session.get("intercepts")

    parameter = request.form.get("parameter")
    confidence_level = float(request.form.get("confidence_level"))

    # Use the slopes or intercepts from the simulations
    if parameter == "slope":
        estimates = np.array(slopes)
        observed_stat = slope
        true_param = beta1
    else:
        estimates = np.array(intercepts)
        observed_stat = intercept
        true_param = beta0

    # TODO 14: Calculate mean and standard deviation of the estimates
    mean_estimate = np.mean(estimates)
    std_estimate = np.std(estimates)

    # TODO 15: Calculate confidence interval for the parameter estimate
    # Use the t-distribution and confidence_level
    # Calculate the t-score for the desired confidence level
    # Approximate z-score based on confidence level
    if confidence_level == 90:
        approx_z_score = 1.645
    elif confidence_level == 95:
        approx_z_score = 1.96
    elif confidence_level == 99:
        approx_z_score = 2.576

    # Calculate the margin of error
    margin_of_error = approx_z_score * (std_estimate / np.sqrt(S))

    ci_lower = mean_estimate - margin_of_error
    ci_upper = mean_estimate + margin_of_error

    # TODO 16: Check if confidence interval includes true parameter
    includes_true =  ci_lower <= true_param <= ci_upper

    # TODO 17: Plot the individual estimates as gray points and confidence interval
    # Plot the mean estimate as a colored point which changes if the true parameter is included
    # Plot the confidence interval as a horizontal line
    # Plot the true parameter value
    plot4_path = "static/plot4.png"
    # Write code here to generate and save the plot
    
    plt.figure(figsize=(10, 5))

    # Plot individual estimates as gray points
    plt.plot(estimates, np.zeros_like(estimates), 'o', color='gray', alpha=0.5, label='Individual Estimates')

    # Plot the mean estimate as a colored point, with color depending on whether it includes the true parameter
    mean_color = 'green' if ci_lower <= true_param <= ci_upper else 'red'
    plt.plot(mean_estimate, 0, 'o', color=mean_color, label='Mean Estimate')

    # Plot the confidence interval as a horizontal line
    plt.hlines(0, ci_lower, ci_upper, color='blue', linewidth=2, label='Confidence Interval')

    # Plot the true parameter value as a dotted green line
    parameter_label = f"True {parameter.capitalize()} Value"
    plt.axvline(true_param, color='green', linestyle='--', linewidth=2, label=parameter_label)

    # Adding labels and legend
    plt.xlabel("Estimate Value")
    plt.yticks([])  # Hide y-axis ticks since we are just plotting points on a line
    plt.title(f"{int(confidence_level)}% Confidence Interval for {parameter.capitalize()}")
    plt.legend()

    # Save the plot
    plot4_path = "static/plot4.png"
    plt.savefig(plot4_path)
    plt.close()

    # Return results to template
    return render_template(
        "index.html",
        plot1="static/plot1.png",
        plot2="static/plot2.png",
        plot4=plot4_path,
        parameter=parameter,
        confidence_level=confidence_level,
        mean_estimate=mean_estimate,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        includes_true=includes_true,
        observed_stat=observed_stat,
        N=N,
        mu=mu,
        sigma2=sigma2,
        beta0=beta0,
        beta1=beta1,
        S=S,
    )


if __name__ == "__main__":
    app.run(debug=True)
