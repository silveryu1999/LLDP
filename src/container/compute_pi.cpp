#include <pybind11/pybind11.h>
#include <iostream>
#include <cmath>
#include <chrono>

#define PRECISION 100000L

/**
 * This function computes pi using work trials for a Monte Carlo method. It's
 * TERRIBLE because it uses a custom, bad, number generator, which has too 
 * much bias to compute a good value a PI. The reason for using the generator
 * is that it does not cause extra memory references, and thus keeps this benchmark
 * 100% CPU intensive. 
 */
double compute_terrible_pi(long work) {
    auto start = std::chrono::system_clock::now();
    work = work * 1000000;
    long rng = (long)&work;
    double terrible_pi = 0.0;
    double x_value, y_value;
    for (long sample=0; sample < work; sample++) {
        rng = (((rng * 214013L + 2531011L) >> 16) & 32767);
        x_value = -0.5 + (rng % PRECISION) / (double)PRECISION;
        rng = (((rng * 214013L + 2531011L) >> 16) & 32767);
        y_value = -0.5 + (rng % PRECISION) / (double)PRECISION;
        terrible_pi += (double)(std::sqrt(x_value*x_value+ y_value*y_value) < 0.5);
    }
    auto end = std::chrono::system_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);
    return double(duration.count()) * 1e-9;
    // std::cout << "terrible pi = " << (terrible_pi/(double)work)/ (0.5*0.5) << "\n";
}

PYBIND11_MODULE(compute_pi, m) {
    m.doc() = "Compute Pi"; // optional module docstring
    m.def("compute_terrible_pi", &compute_terrible_pi, pybind11::arg("work") = 1000, "A function which calculates terrible Pi");
}