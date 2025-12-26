project('mcu_app', ['c', 'cpp'], default_options: ['default_library=static'])

app = library('app',
    'src/lib.c',
    'src/lib.cc',
)

app_dep = declare_dependency(
    link_with: app,
    include_directories: include_directories('src'),
)

gtest = subproject('gtest').get_variable('gtest_main_dep')
my_tests = executable('my_tests',
    ['test/test.cc'],
    dependencies: [app_dep, gtest],
    override_options: 'cpp_std=c++17',
)
test('gtest suite', my_tests, verbose: true)
