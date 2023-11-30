#------------------------------------------------------------------------
# hdot: CMakeLists.txt
#------------------------------------------------------------------------
cmake_minimum_required(VERSION 3.0)
set(PROJECT_NAME hdot)

project(${PROJECT_NAME})
set(${PROJECT_NAME} VERSION MAJOR 1)
set(${PROJECT_NAME} VERSION MINOR 0)
set(DESTINATION $ENV{SWDIR})

set(CMAKE_INSTALL_PREFIX ${DESTINATION})

set(progs
  scripts/sddgen.py
  scripts/sddtest1.py)

# Installation
install(DIRECTORY ${CMAKE_SOURCE_DIR}/hdot
  DESTINATION python
  FILES_MATCHING PATTERN "*.py"
  )

foreach(prog ${progs})
  install(PROGRAMS ${prog} DESTINATION bin)
endforeach()

