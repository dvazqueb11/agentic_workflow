from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout


class ProjectBoostConan(ConanFile):
    name = "project-boost-self-healing-ci"
    version = "0.1.0"
    settings = "os", "compiler", "build_type", "arch"
    requires = "gtest/1.14.0"

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        toolchain = CMakeToolchain(self)
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        pass

    def package_info(self):
        pass
