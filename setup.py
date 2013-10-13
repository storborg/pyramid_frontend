from setuptools import setup


# The following executables are also required in PATH.
#   jpegoptim
#   pngcrush
#   optipng
#   convert (from GraphicsMagick or ImageMagick)

setup(name='pyramid_frontend',
      version='0.1',
      description='Themes, image filtering, and frontend asset handling.',
      long_description='',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Framework :: Pyramid',
      ],
      keywords='pyramid themes frontend assets',
      url='http://github.com/cartlogic/pyramid_frontend',
      author='Scott Torborg',
      author_email='scott@cartlogic.com',
      install_requires=[
          'Pyramid>=1.4.5',
          'Pillow>=2.1.0',      # Provides PIL
          'Mako>=0.9.0',
          # These are for tests.
          'coverage',
          'nose>=1.1',
          'nose-cover3',
      ],
      license='MIT',
      packages=['pyramid_frontend'],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
