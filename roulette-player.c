#include <Python.h>

typedef struct {
    PyObject_HEAD
    PyObject *history;      // Python list of game results in cents
    PyObject *bet_sizes;    // Python list of bet amounts in cents
    PyObject *numbers_bet;  // Python list of numbers bet on
    long bankroll;         // Current bankroll in cents
} PlayerObject;

static void
Player_dealloc(const PlayerObject *self)
{
    Py_XDECREF(self->history);
    Py_XDECREF(self->bet_sizes);
    Py_XDECREF(self->numbers_bet);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *
    Player_new(PyTypeObject *type, PyObject *args __attribute__((unused)), PyObject *keywords __attribute__((unused)))
{
    PlayerObject *self = (PlayerObject *) type->tp_alloc(type, 0);
    if (self != NULL) {
        self->history = PyList_New(0);
        self->bet_sizes = PyList_New(0);
        self->numbers_bet = PyList_New(0);
        
        if (self->history == NULL || self->bet_sizes == NULL || self->numbers_bet == NULL) {
            Py_DECREF(self);
            return NULL;
        }
        self->bankroll = 0;
    }
    return (PyObject *) self;
}

static int
Player_init(PlayerObject *self, PyObject *args, PyObject *keywords)
{
    static char *kwlist[] = {"initial_bankroll", NULL};
    long initial_bankroll = 100000;  // Default value: 1000.00 in cents

    if (!PyArg_ParseTupleAndKeywords(args, keywords, "|l", kwlist, &initial_bankroll))
        return -1;

    self->bankroll = initial_bankroll;
    return 0;
}

static PyObject *
Player_add_game(PlayerObject *self, PyObject *args, PyObject *keywords)
{
    static char *kwlist[] = {"result", "bet_size", "number", NULL};
    long result, bet_size;
    int number;

    if (!PyArg_ParseTupleAndKeywords(args, keywords, "lli", kwlist, &result, &bet_size, &number))
        return NULL;

    PyObject *result_obj = PyLong_FromLong(result);
    PyObject *bet_size_obj = PyLong_FromLong(bet_size);
    PyObject *number_obj = PyLong_FromLong(number);

    if (result_obj == NULL || bet_size_obj == NULL || number_obj == NULL) {
        Py_XDECREF(result_obj);
        Py_XDECREF(bet_size_obj);
        Py_XDECREF(number_obj);
        return NULL;
    }

    if (PyList_Append(self->history, result_obj) < 0 ||
        PyList_Append(self->bet_sizes, bet_size_obj) < 0 ||
        PyList_Append(self->numbers_bet, number_obj) < 0) {
        Py_DECREF(result_obj);
        Py_DECREF(bet_size_obj);
        Py_DECREF(number_obj);
        return NULL;
    }

    self->bankroll += result;

    Py_DECREF(result_obj);
    Py_DECREF(bet_size_obj);
    Py_DECREF(number_obj);
    Py_RETURN_NONE;
}

static PyObject *
Player_get_history(const PlayerObject *self, PyObject *Py_UNUSED(ignored))
{
    return PyList_GetSlice(self->history, 0, PyList_Size(self->history));
}

static PyObject *
Player_get_bet_sizes(const PlayerObject *self, PyObject *Py_UNUSED(ignored))
{
    return PyList_GetSlice(self->bet_sizes, 0, PyList_Size(self->bet_sizes));
}

static PyObject *
Player_get_numbers_bet(const PlayerObject *self, PyObject *Py_UNUSED(ignored))
{
    return PyList_GetSlice(self->numbers_bet, 0, PyList_Size(self->numbers_bet));
}

static PyObject *
Player_get_bankroll(const PlayerObject *self, PyObject *Py_UNUSED(ignored))
{
    return PyLong_FromLong(self->bankroll);
}

static PyObject *
Player_get_stats(const PlayerObject *self, PyObject *Py_UNUSED(ignored))
{
    PyObject *stats = PyDict_New();
    if (stats == NULL)
        return NULL;

    Py_ssize_t num_games = PyList_Size(self->history);
    long total_profit = 0;
    long max_profit = 0;
    long max_loss = 0;
    int wins = 0;

    for (Py_ssize_t i = 0; i < num_games; i++) {
        PyObject *result = PyList_GetItem(self->history, i);
        long profit = PyLong_AsLong(result);
        
        total_profit += profit;
        if (profit > max_profit) max_profit = profit;
        if (profit < max_loss) max_loss = profit;
        if (profit > 0) wins++;
    }

    PyDict_SetItemString(stats, "total_games", PyLong_FromSsize_t(num_games));
    PyDict_SetItemString(stats, "total_profit", PyLong_FromLong(total_profit));
    PyDict_SetItemString(stats, "max_profit", PyLong_FromLong(max_profit));
    PyDict_SetItemString(stats, "max_loss", PyLong_FromLong(max_loss));
    PyDict_SetItemString(stats, "wins", PyLong_FromLong(wins));
    if (num_games > 0) {
        PyDict_SetItemString(stats, "win_rate",
            PyFloat_FromDouble((double)wins / (double)num_games * 100.0));
    }
    return stats;
}

static PyMethodDef Player_methods[] = {
    {"add_game", (PyCFunction) Player_add_game, METH_VARARGS | METH_KEYWORDS,
     "Add a game result with bet size (in cents) and number"},
    {"get_history", (PyCFunction) Player_get_history, METH_NOARGS,
     "Get the complete history of game results (in cents)"},
    {"get_bet_sizes", (PyCFunction) Player_get_bet_sizes, METH_NOARGS,
     "Get the history of bet sizes (in cents)"},
    {"get_numbers_bet", (PyCFunction) Player_get_numbers_bet, METH_NOARGS,
     "Get the history of numbers bet on"},
    {"get_bankroll", (PyCFunction) Player_get_bankroll, METH_NOARGS,
     "Get current bankroll (in cents)"},
    {"get_stats", (PyCFunction) Player_get_stats, METH_NOARGS,
     "Get player statistics (monetary values in cents)"},
    {NULL}  /* Sentinel */
};

static PyTypeObject PlayerType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "casino_player.Player",
    .tp_doc = PyDoc_STR("Roulette player object to track game history and statistics (all monetary values in cents)"),
    .tp_basicsize = sizeof(PlayerObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Player_new,
    .tp_init = (initproc) Player_init,
    .tp_dealloc = (destructor) Player_dealloc,
    .tp_methods = Player_methods,
};

static PyModuleDef casino_player_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "casino_player",
    .m_doc = "Module for tracking roulette player statistics (all monetary values in cents)",
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit_casino_player(void)
{
    if (PyType_Ready(&PlayerType) < 0)
        return NULL;

    PyObject *m = PyModule_Create(&casino_player_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&PlayerType);
    if (PyModule_AddObject(m, "Player", (PyObject *) &PlayerType) < 0) {
        Py_DECREF(&PlayerType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
