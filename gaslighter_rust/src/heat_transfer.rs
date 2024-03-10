use std::env::current_exe;

use pyo3::prelude::*;

fn euler_explicit(
    diffusivity: f64,
    n2: f64,
    n1: f64,
    n0: f64,
    dx: f64,
    dt: f64
) -> f64{

    let heat_comp = n2 - (2.0 * n1) + n0;

    return n0 + (diffusivity * dt) * (heat_comp / dx.powf(2.0))
}



/// Solvers the explicit finite diffrence method
/// for the heat equation. Returns the temperature as history of time dx [final two elements in the data]
/// Source: https://www-udc.ig.utexas.edu/external/becker/teaching/557/problem_sets/problem_set_fd_explicit.pdf
#[pyfunction]
pub fn fdm_1d(
    intial_temps: Vec<f64>,
    dx: f64,
    time: f64,
    diffusivity: f64
) -> Py<PyAny> {

    // Stability Estimate
    let dt = dx.powf(2.0) / (4.0 * diffusivity);

    let max_temp_index = intial_temps.len();
    let time_index = (time / dt) as usize;

    // Create the temp history
    let mut temp_history = vec![vec![0.0; max_temp_index + 2]];
    let mut new_t = 404.0;
    let mut current_temps = intial_temps.clone();
    current_temps.push(0.0);
    current_temps.push(0.0);
    temp_history[0] = current_temps;


    for i in 0..time_index{
        if i == 0{
            continue
        }

        let mut current_temps = temp_history[i - 1].clone();

        for j in 0..current_temps.len(){

            // Add dx on the end
            if j == current_temps.len() - 1{
                current_temps[j] = dx;
                continue
            }

            // Add time on the end
            if j == current_temps.len() - 2{
                current_temps[j] = i as f64 * dt;
                continue
            }

            // Skip Boundary
            if j == 0 || j == (max_temp_index - 1){
                continue
            }

            new_t  = euler_explicit(
                diffusivity,
                current_temps[j + 1],
                current_temps[j],
                current_temps[j - 1],
                dx,
                dt
            );
            current_temps[j] = new_t;

        }

        temp_history.push(current_temps);
    }

    // Do some weird shit to get it back to python
    return Python::with_gil(|py|{
        temp_history.to_object(py)
    });
}
