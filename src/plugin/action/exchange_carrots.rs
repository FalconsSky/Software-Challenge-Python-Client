use pyo3::*;

use crate::plugin::game_state::GameState;

#[pyclass]
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Hash)]
pub struct ExchangeCarrots {
    #[pyo3(get, set)]
    amount: i32,
}

#[pymethods]
impl ExchangeCarrots {
    #[new]
    #[must_use]
    pub fn new(amount: i32) -> Self {
        Self { amount }
    }

    pub fn perform(&self, state: &mut GameState) -> Result<(), PyErr> {
        let mut current = state.clone_current_player();
        current.exchange_carrots(state, self.amount)?;
        Ok(())
    }
}
