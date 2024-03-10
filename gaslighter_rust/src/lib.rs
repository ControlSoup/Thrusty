use pyo3::prelude::*;
pub mod heat_transfer;


/// A Python module implemented in Rust.
#[pymodule]
fn gaslighter_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(heat_transfer::fdm_1d, m)?)?;
    Ok(())
}
