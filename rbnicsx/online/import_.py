# Copyright (C) 2021-2022 by the RBniCSx authors
#
# This file is part of RBniCSx.
#
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Online backend to import matrices and vectors."""

import typing

import mpi4py
import petsc4py

from rbnicsx._backends.import_ import (
    import_matrices as import_matrices_super, import_matrix as import_matrix_super,
    import_vector as import_vector_super, import_vectors as import_vectors_super)
from rbnicsx._backends.online_tensors import (
    create_online_matrix as create_matrix, create_online_matrix_block as create_matrix_block,
    create_online_vector as create_vector, create_online_vector_block as create_vector_block)


def import_matrix(M: int, N: int, directory: str, filename: str) -> petsc4py.PETSc.Mat:
    """
    Import a dense petsc4py.PETSc.Mat from file.

    Parameters
    ----------
    M, N : int
        Dimension of the online matrix.
    directory : str
        Directory where to import the matrix from.
    filename : str
        Name of the file where to import the matrix from.

    Returns
    -------
    petsc4py.PETSc.Mat
        Matrix imported from file.
    """
    return import_matrix_super(lambda: create_matrix(M, N), mpi4py.MPI.COMM_SELF, directory, filename)


def import_matrix_block(M: typing.List[int], N: typing.List[int], directory: str, filename: str) -> petsc4py.PETSc.Mat:
    """
    Import a dense petsc4py.PETSc.Mat from file.

    Parameters
    ----------
    M, N : typing.List[int]
        Dimension of the blocks of the matrix.
    directory : str
        Directory where to import the matrix from.
    filename : str
        Name of the file where to import the matrix from.

    Returns
    -------
    petsc4py.PETSc.Mat
        Matrix imported from file.
    """
    return import_matrix_super(lambda: create_matrix_block(M, N), mpi4py.MPI.COMM_SELF, directory, filename)


def import_matrices(M: int, N: int, directory: str, filename: str) -> typing.List[petsc4py.PETSc.Mat]:
    """
    Import a list of dense petsc4py.PETSc.Mat from file.

    Parameters
    ----------
    M, N : int
        Dimension of each online matrix.
    directory : str
        Directory where to import the matrix from.
    filename : str
        Name of the file where to import the matrix from.

    Returns
    -------
    typing.List[petsc4py.PETSc.Mat]
        Matrices imported from file.
    """
    return import_matrices_super(lambda: create_matrix(M, N), mpi4py.MPI.COMM_SELF, directory, filename)


def import_matrices_block(
    M: typing.List[int], N: typing.List[int], directory: str, filename: str
) -> typing.List[petsc4py.PETSc.Mat]:
    """
    Import a list of dense petsc4py.PETSc.Mat from file.

    Parameters
    ----------
    M, N : typing.List[int]
        Dimension of the blocks of the matrix.
    directory : str
        Directory where to import the matrix from.
    filename : str
        Name of the file where to import the matrix from.

    Returns
    -------
    typing.List[petsc4py.PETSc.Mat]
        Matrices imported from file.
    """
    return import_matrices_super(lambda: create_matrix_block(M, N), mpi4py.MPI.COMM_SELF, directory, filename)


def import_vector(N: int, directory: str, filename: str) -> petsc4py.PETSc.Vec:
    """
    Import a sequential petsc4py.PETSc.Vec from file.

    Parameters
    ----------
    N : int
        Dimension of the online vector.
    directory : str
        Directory where to import the vector from.
    filename : str
        Name of the file where to import the vector from.

    Returns
    -------
    petsc4py.PETSc.Vec
        Vector imported from file.
    """
    return import_vector_super(lambda: create_vector(N), mpi4py.MPI.COMM_SELF, directory, filename)


def import_vector_block(N: typing.List[int], directory: str, filename: str) -> petsc4py.PETSc.Vec:
    """
    Import a sequential petsc4py.PETSc.Vec from file.

    Parameters
    ----------
    N : typing.List[int]
        Dimension of the blocks of the vector.
    directory : str
        Directory where to import the vector from.
    filename : str
        Name of the file where to import the vector from.

    Returns
    -------
    petsc4py.PETSc.Vec
        Vector imported from file.
    """
    return import_vector_super(lambda: create_vector_block(N), mpi4py.MPI.COMM_SELF, directory, filename)


def import_vectors(N: int, directory: str, filename: str) -> typing.List[petsc4py.PETSc.Vec]:
    """
    Import a list of sequential petsc4py.PETSc.Vec from file.

    Parameters
    ----------
    N : int
        Dimension of the online vector.
    directory : str
        Directory where to import the vector from.
    filename : str
        Name of the file where to import the vector from.

    Returns
    -------
    typing.List[petsc4py.PETSc.Vec]
        Vectors imported from file.
    """
    return import_vectors_super(lambda: create_vector(N), mpi4py.MPI.COMM_SELF, directory, filename)


def import_vectors_block(N: typing.List[int], directory: str, filename: str) -> typing.List[petsc4py.PETSc.Vec]:
    """
    Import a list of sequential petsc4py.PETSc.Vec from file.

    Parameters
    ----------
    N : typing.List[int]
        Dimension of the blocks of the vector.
    directory : str
        Directory where to import the vector from.
    filename : str
        Name of the file where to import the vector from.

    Returns
    -------
    typing.List[petsc4py.PETSc.Vec]
        Vectors imported from file.
    """
    return import_vectors_super(lambda: create_vector_block(N), mpi4py.MPI.COMM_SELF, directory, filename)
