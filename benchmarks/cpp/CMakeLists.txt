cmake_minimum_required(VERSION 3.20)
project(quant_lang_shootout_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
add_compile_options(-Wall -Wextra -Wpedantic)

add_library(quant_lang_shootout INTERFACE)
target_include_directories(quant_lang_shootout INTERFACE ${CMAKE_CURRENT_SOURCE_DIR})

add_executable(bench_main bench_main.cpp)
target_link_libraries(bench_main PRIVATE quant_lang_shootout)

add_executable(test_benchmarks test_benchmarks.cpp)
target_link_libraries(test_benchmarks PRIVATE quant_lang_shootout)

enable_testing()
add_test(NAME cpp_unit_tests COMMAND test_benchmarks)
