import os.path
import scipy.io

def read_mat(mat_filename):
    cur_path = os.path.dirname(__file__)
    mat_file_path = os.path.join(cur_path, mat_filename)
    imported = scipy.io.loadmat(mat_file_path)
    return imported

if __name__ == "__main__":
    pass