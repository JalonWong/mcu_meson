project(
    'mcu_app',
    ['c', 'cpp'],
    default_options: [
        'default_library=static',
        'optimization=1',
        'debug=true',
    ],
)

if meson.is_cross_build()
    library(
        'app',
        'src/lib.c',
        'src/lib.cc',
    )
else
    test(
        'gtest suite',
        executable(
            'my_tests',
            ['tests/test.cc', 'src/lib.c', 'src/lib.cc'],
            include_directories: ['src'],
            dependencies: [
                dependency('gtest_main'),
            ],
            override_options: ['cpp_std=c++17'],
        ),
        verbose: true,
    )
endif
