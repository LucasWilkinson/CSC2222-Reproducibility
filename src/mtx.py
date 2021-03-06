import numpy  as np
import matplotlib.pyplot as plt
from copy import deepcopy
from collections import namedtuple
from scipy.sparse import csr_matrix

CSRPattern = namedtuple('CSRPattern', 
                        ['nrows', 'ncols', 'nnz', 'row_ptrs', 'col_indices'])

# Read the custom sputnick data file structure, its a pattern only file 
# format so contains no values
#   line 1: nrows, ncols, nnz
#   line 2: row_ptrs ... (space delimited)
#   line 3: col_indices ... (space delimited)
def read_pattern(filepath):
    with open(filepath) as file:
        lines = [file.readline() for _ in range(3)]
        nrows, ncols, nnz = [int(x) for x in lines[0].split(',')]
        return CSRPattern(nrows=nrows, ncols=ncols, nnz=nnz,
            row_ptrs=np.fromstring(lines[1], dtype=int, sep=" "),
            col_indices=np.fromstring(lines[2], dtype=int, sep=" ")
        )
    return None

# Convert the pattern to a scipy CSR matrix with 1s for all the values to 
# enable using scipy libraries/plotting/etc.
def pattern_to_scipy_csr(csr_pattern: CSRPattern):
    nnz = len(csr_pattern.col_indices)
    return csr_matrix(([1] * nnz, csr_pattern.col_indices, csr_pattern.row_ptrs),
                      (csr_pattern.nrows, csr_pattern.ncols))


def pattern_to_dense(csr_pattern: CSRPattern):
    result = np.zeros((csr_pattern.nrows, csr_pattern.ncols))
    for i in range(len(csr_pattern.row_ptrs)-1):
        start, end = csr_pattern.row_ptrs[i], csr_pattern.row_ptrs[i+1]
        for j in range(start, end):
            try:
                result[i, csr_pattern.col_indices[j]] = 1
            except:
                raise ValueError("error!!! i: {}, j: {}".format(i, csr_pattern.col_indices[j]))
                    
    return result

 

def get_mtx(path):
    with open(path, 'r') as f:
        contents = f.readlines()
        contents = [i.strip() for i in contents]
        info, row_pt, col_indx = contents
        row_pt = row_pt.split(" ")
        row_pt = [int(i) for i in row_pt]
        col_indx = col_indx.split(" ")
        col_indx = [int(i) for i in col_indx]

        info = info.split(", ")
        info = [int(i) for i in info]
        n_row, n_col, nnz = info
        result = np.zeros((n_row, n_col))
        for i in range(len(row_pt) - 1):
            start, end = row_pt[i], row_pt[i+1]
            for j in range(start, end):
                try:
                    result[i, col_indx[j]] = 1
                except:
                    raise ValueError("error!!! i: {}, j: {}".format(i, col_indx[j]))
                    
    return result

 

def dense_to_sparse(matrix):
  """Converts dense numpy matrix to a csr sparse matrix."""
  assert len(matrix.shape) == 2

  # Extract the nonzero values.
  values = matrix.compress((matrix != 0).flatten())

  # Calculate the offset of each row.
  mask = (matrix != 0).astype(np.int32)
  row_offsets = np.concatenate(([0], np.cumsum(np.add.reduce(mask, axis=1))),
                               axis=0)

  # Create the row indices and sort them.
  row_indices = np.argsort(-1 * np.diff(row_offsets))

  # Extract the column indices for the nonzero values.
  x = mask * (np.arange(matrix.shape[1]) + 1)
  column_indices = x.compress((x != 0).flatten())
  column_indices = column_indices - 1

  # Cast the desired precision.
  values = values.astype(np.float32)
  row_indices, row_offsets, column_indices = [
      x.astype(np.uint32) for x in
      [row_indices, row_offsets, column_indices]
  ]
  return values, row_indices, row_offsets, column_indices


if __name__ == "__main__":
    path = '/mnt/benchmark_cpp/dlmc/rn50/extended_magnitude_pruning/0.8/bottleneck_1_block_group_projection_block_group1.smtx'
    mtx = get_mtx(path)
    plt.imshow(mtx)
    plt.savefig("./shit.pdf")
