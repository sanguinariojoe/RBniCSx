# Copyright (C) 2021-2022 by the RBniCSx authors
#
# This file is part of RBniCSx.
#
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Tests for rbnicsx.backends.projection module."""

import typing

import dolfinx.fem
import dolfinx.mesh
import mpi4py
import numpy as np
import pytest
import ufl

import rbnicsx.backends


@pytest.fixture
def mesh() -> dolfinx.mesh.Mesh:
    """Generate a unit square mesh for use in tests in this file."""
    comm = mpi4py.MPI.COMM_WORLD
    return dolfinx.mesh.create_unit_square(comm, 2 * comm.size, 2 * comm.size)


@pytest.fixture
def functions_list(mesh: dolfinx.mesh.Mesh) -> rbnicsx.backends.FunctionsList:
    """Generate a rbnicsx.backends.FunctionsList with several entries."""
    V = dolfinx.fem.FunctionSpace(mesh, ("Lagrange", 1))
    functions_list = rbnicsx.backends.FunctionsList(V)
    for i in range(14):
        function = dolfinx.fem.Function(V)
        with function.vector.localForm() as function_local:
            function_local.set(i + 1)
        functions_list.append(function)
    return functions_list


def test_projection_vector(mesh: dolfinx.mesh.Mesh, functions_list: rbnicsx.backends.FunctionsList) -> None:
    """Test projection of a linear form onto the reduced basis."""
    basis_functions = functions_list[:2]

    V = dolfinx.fem.FunctionSpace(mesh, ("Lagrange", 1))
    v = ufl.TestFunction(V)
    linear_form = ufl.inner(1, v) * ufl.dx

    online_vec = rbnicsx.backends.project_vector(linear_form, basis_functions)
    assert online_vec.size == 2
    assert np.allclose(online_vec.array, [1, 2])

    online_vec2 = rbnicsx.backends.project_vector(0.4 * linear_form, basis_functions)
    rbnicsx.backends.project_vector(online_vec2, 0.6 * linear_form, basis_functions)
    assert online_vec2.size == 2
    assert np.allclose(online_vec2.array, online_vec.array)


def test_projection_vector_block(mesh: dolfinx.mesh.Mesh, functions_list: rbnicsx.backends.FunctionsList) -> None:
    """Test projection of a list of linear forms onto the reduced basis."""
    basis_functions = [functions_list[:2], functions_list[2:5]]

    V = dolfinx.fem.FunctionSpace(mesh, ("Lagrange", 1))
    v = ufl.TestFunction(V)
    linear_forms = [ufl.inner(10**i, v) * ufl.dx for i in range(2)]

    online_vec = rbnicsx.backends.project_vector_block(linear_forms, basis_functions)
    assert online_vec.size == 5
    assert np.allclose(online_vec[0:2], [1, 2])
    assert np.allclose(online_vec[2:5], np.array([3, 4, 5]) * 10)

    online_vec2 = rbnicsx.backends.project_vector_block(
        [0.4 * linear_form for linear_form in linear_forms], basis_functions)
    rbnicsx.backends.project_vector_block(
        online_vec2, [0.6 * linear_form for linear_form in linear_forms], basis_functions)
    assert online_vec2.size == 5
    assert np.allclose(online_vec2.array, online_vec.array)


def test_projection_matrix_galerkin(
    mesh: dolfinx.mesh.Mesh, functions_list: rbnicsx.backends.FunctionsList, to_dense_matrix: typing.Callable
) -> None:
    """Test projection of a bilinear form onto the reduced basis (for use in Galerkin methods)."""
    basis_functions = functions_list[:2]

    V = dolfinx.fem.FunctionSpace(mesh, ("Lagrange", 1))
    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)
    bilinear_form = ufl.inner(u, v) * ufl.dx

    online_mat = rbnicsx.backends.project_matrix(bilinear_form, basis_functions)
    assert online_mat.size == (2, 2)
    assert np.allclose(online_mat[0, :], [1, 2])
    assert np.allclose(online_mat[1, :], np.array([1, 2]) * 2)

    online_mat2 = rbnicsx.backends.project_matrix(0.4 * bilinear_form, basis_functions)
    rbnicsx.backends.project_matrix(online_mat2, 0.6 * bilinear_form, basis_functions)
    assert online_mat2.size == (2, 2)
    assert np.allclose(to_dense_matrix(online_mat2), to_dense_matrix(online_mat))


def test_projection_matrix_petrov_galerkin(
    mesh: dolfinx.mesh.Mesh, functions_list: rbnicsx.backends.FunctionsList, to_dense_matrix: typing.Callable
) -> None:
    """Test projection of a bilinear form onto the reduced basis (for use in Petrov-Galerkin methods)."""
    basis_functions = (functions_list[:2], functions_list[2:5])

    V = dolfinx.fem.FunctionSpace(mesh, ("Lagrange", 1))
    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)
    bilinear_form = ufl.inner(u, v) * ufl.dx

    online_mat = rbnicsx.backends.project_matrix(bilinear_form, basis_functions)
    assert online_mat.size == (2, 3)
    assert np.allclose(online_mat[0, :], [3, 4, 5])
    assert np.allclose(online_mat[1, :], np.array([3, 4, 5]) * 2)

    online_mat2 = rbnicsx.backends.project_matrix(0.4 * bilinear_form, basis_functions)
    rbnicsx.backends.project_matrix(online_mat2, 0.6 * bilinear_form, basis_functions)
    assert online_mat2.size == (2, 3)
    assert np.allclose(to_dense_matrix(online_mat2), to_dense_matrix(online_mat))


def test_projection_matrix_block_galerkin(
    mesh: dolfinx.mesh.Mesh, functions_list: rbnicsx.backends.FunctionsList, to_dense_matrix: typing.Callable
) -> None:
    """Test projection of a matrix of bilinear forms onto the reduced basis (for use in Galerkin methods)."""
    basis_functions = [functions_list[:2], functions_list[2:5]]

    V = dolfinx.fem.FunctionSpace(mesh, ("Lagrange", 1))
    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)
    bilinear_forms = [[10**i * (-1)**j * ufl.inner(u, v) * ufl.dx for j in range(2)] for i in range(2)]

    online_mat = rbnicsx.backends.project_matrix_block(bilinear_forms, basis_functions)
    assert online_mat.size == (5, 5)
    assert np.allclose(online_mat[0, 0:2], [1, 2])
    assert np.allclose(online_mat[0, 2:5], np.array([3, 4, 5]) * -1)
    assert np.allclose(online_mat[1, 0:2], np.array([1, 2]) * 2)
    assert np.allclose(online_mat[1, 2:5], np.array([3, 4, 5]) * -2)
    assert np.allclose(online_mat[2, 0:2], np.array([1, 2]) * 30)
    assert np.allclose(online_mat[2, 2:5], np.array([3, 4, 5]) * -30)
    assert np.allclose(online_mat[3, 0:2], np.array([1, 2]) * 40)
    assert np.allclose(online_mat[3, 2:5], np.array([3, 4, 5]) * -40)
    assert np.allclose(online_mat[4, 0:2], np.array([1, 2]) * 50)
    assert np.allclose(online_mat[4, 2:5], np.array([3, 4, 5]) * -50)

    online_mat2 = rbnicsx.backends.project_matrix_block(
        [[0.4 * bilinear_form for bilinear_form in bilinear_forms_] for bilinear_forms_ in bilinear_forms],
        basis_functions)
    rbnicsx.backends.project_matrix_block(
        online_mat2,
        [[0.6 * bilinear_form for bilinear_form in bilinear_forms_] for bilinear_forms_ in bilinear_forms],
        basis_functions)
    assert online_mat2.size == (5, 5)
    assert np.allclose(to_dense_matrix(online_mat2), to_dense_matrix(online_mat))


def test_projection_matrix_block_petrov_galerkin(
    mesh: dolfinx.mesh.Mesh, functions_list: rbnicsx.backends.FunctionsList, to_dense_matrix: typing.Callable
) -> None:
    """Test projection of a matrix of bilinear forms onto the reduced basis (for use in Petrov-Galerkin methods)."""
    basis_functions = ([functions_list[:2], functions_list[2:5]], [functions_list[5:9], functions_list[9:14]])

    V = dolfinx.fem.FunctionSpace(mesh, ("Lagrange", 1))
    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)
    bilinear_forms = [[10**i * (-1)**j * ufl.inner(u, v) * ufl.dx for j in range(2)] for i in range(2)]

    online_mat = rbnicsx.backends.project_matrix_block(bilinear_forms, basis_functions)
    assert online_mat.size == (5, 9)
    assert np.allclose(online_mat[0, 0:4], [6, 7, 8, 9])
    assert np.allclose(online_mat[0, 4:9], np.array([10, 11, 12, 13, 14]) * -1)
    assert np.allclose(online_mat[1, 0:4], np.array([6, 7, 8, 9]) * 2)
    assert np.allclose(online_mat[1, 4:9], np.array([10, 11, 12, 13, 14]) * -2)
    assert np.allclose(online_mat[2, 0:4], np.array([6, 7, 8, 9]) * 30)
    assert np.allclose(online_mat[2, 4:9], np.array([10, 11, 12, 13, 14]) * -30)
    assert np.allclose(online_mat[3, 0:4], np.array([6, 7, 8, 9]) * 40)
    assert np.allclose(online_mat[3, 4:9], np.array([10, 11, 12, 13, 14]) * -40)
    assert np.allclose(online_mat[4, 0:4], np.array([6, 7, 8, 9]) * 50)
    assert np.allclose(online_mat[4, 4:9], np.array([10, 11, 12, 13, 14]) * -50)

    online_mat2 = rbnicsx.backends.project_matrix_block(
        [[0.4 * bilinear_form for bilinear_form in bilinear_forms_] for bilinear_forms_ in bilinear_forms],
        basis_functions)
    rbnicsx.backends.project_matrix_block(
        online_mat2,
        [[0.6 * bilinear_form for bilinear_form in bilinear_forms_] for bilinear_forms_ in bilinear_forms],
        basis_functions)
    assert online_mat2.size == (5, 9)
    assert np.allclose(to_dense_matrix(online_mat2), to_dense_matrix(online_mat))
