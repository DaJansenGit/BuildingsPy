#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import unittest
import os

# To run this test, navigate to the BuildingsPy folder, then type
# python buildingspy/tests/test_development_regressiontest.py


class Test_regressiontest_openmodelica_Tester(unittest.TestCase):
    """
       This class contains the unit tests for
       :mod:`buildingspy.regressiontest.Tester` for openmodelica.
    """

    def test_unit_test_log_file(self):
        import buildingspy.development.regressiontest as r
        rt = r.Tester(check_html=False, tool="openmodelica")
        self.assertEqual('unitTests-openmodelica.log', rt.get_unit_test_log_file())

    @staticmethod
    def _write_test(content):
        """ Write a unit test for a model with the content `content`
            in a temporary directory and return the name of this directory.
        """
        import os
        import tempfile

        dir_name = os.path.join(tempfile.mkdtemp(prefix='tmp-BuildingsPy-unittests-'), "TestLib")
        script_dir = os.path.join(dir_name, "Resources", "Scripts", "Dymola")
        mo_name = "Test"
        mo_content = """within TestLib;
          model Test
            {}
            annotation (experiment(Tolerance=1e-6, StopTime=3600));
          end Test;
        """.format(content)

        # Create directory for mos scripts
        os.makedirs(script_dir)
        # Write mos file
        with open(os.path.join(script_dir, mo_name + ".mos"), mode="w", encoding="utf-8") as fil:
            con = """
simulateModel("TestLib.{}", tolerance=1e-6, stopTime=1.0, method="CVode", resultFile="test");""".format(mo_name)
            con = con + """
createPlot(id=1, y={"Test.x"});
"""
            fil.write(con)
        # Write mo file
        with open(os.path.join(dir_name, mo_name + ".mo"), mode="w", encoding="utf-8") as fil:
            fil.write(mo_content)
        # Write top-level package
        with open(os.path.join(dir_name, 'package.mo'), mode="w", encoding="utf-8") as fil:
            mo = """
            within;
            package TestLib
            end TestLib;
"""
            fil.write(mo)
        # Write top-level package.order
        with open(os.path.join(dir_name, 'package.order'), mode="w", encoding="utf-8") as fil:
            mo = """TestLib"""
            fil.write(mo)
        return dir_name

    def test_regressiontest_diagnostics(self):
        """ Test that warnings and errors reported by openmodelica are reported.
        """
        import shutil
        import buildingspy.development.regressiontest as r

        tests = [
            {'ret_val': 0,
             'mo_content': """parameter Real x = 0;""",
             'description': "Correct model."},
            # Commented, see comment in error_dictionary_openmodelica.py
            # {'ret_val': 2,
            # 'mo_content': """parameter Real x(each unit="m") = 0;""",
            # 'description': "Wrong each on scalar."},
            # {'ret_val': 2,
            # 'mo_content': """Modelica.Blocks.Sources.Constant b(each k=0) ;""",
            # 'description': "Wrong each on scalar component."},
            {'ret_val': 1,
             'mo_content': """Modelica.Blocks.Sources.Constant b[2](k=0) ;""",
             'description': "Missing each on array of components."},
            {'ret_val': 0,
             'mo_content': """
                              Real x;
                              equation
                              Modelica.Math.exp(x)=1;""",
             'description': "Missing start value, which should be ignored."},
            {'ret_val': 0,
             'mo_content': """
                              Real x(start=0);
                              equation
                              der(x)^3 = 0;""",
             'description': "Missing start value for der(x), which should be ignored."},
            {'ret_val': 1,
             'mo_content': """parameter Real[2] x(unit="m") = {0, 0};
                                    parameter Real y(each unit="m") = 0;""",
             'description': "Two errors."},
            {'ret_val': 1,
             'mo_content': """x; """,
             'description': "Syntax error that should cause a failure in translation."},
            {'ret_val': 1,
             'mo_content': """Real x(start=0);
                                    equation
                                      Modelica.Math.exp(x)=-1;""",
             'description': "Model that has no solution."}
        ]
        # Run all test cases
        for test in tests:
            des = test['description']
            print("*** Running test for '{}'".format(des))
            mo_content = test['mo_content']
            dir_name = self._write_test(mo_content)
            rt = r.Tester(skip_verification=True, check_html=False, tool="openmodelica")
            rt.setLibraryRoot(dir_name)
            rt.deleteTemporaryDirectories(False)

#                # This test must raise an exception
#                self.assertRaises(ValueError,
#                    rt.setLibraryRoot, "this_is_not_the_root_dir_of_a_library")
#

            ret_val = rt.run()
            # Check return value to see if test succeeded
            self.assertEqual(
                test['ret_val'],
                ret_val,
                f"Test for '{des}' failed, return value {ret_val}, expected {test['ret_val']}")
            # Get parent dir of dir_name, because dir_name contains the Modelica library name
            par = os.path.split(dir_name)[0]
            os.remove(rt.get_unit_test_log_file())
            shutil.rmtree(par)

    def test_regressiontest(self):
        import buildingspy.development.regressiontest as r
        rt = r.Tester(skip_verification=True, check_html=False, tool="openmodelica")
        myMoLib = os.path.join("buildingspy", "tests", "MyModelicaLibrary")
        rt.deleteTemporaryDirectories(True)
        rt.setLibraryRoot(myMoLib)
        ret_val = rt.run()
        # Check return value to see if test suceeded
        self.assertEqual(0, ret_val, "Test failed with return value {}".format(ret_val))
        # Delete temporary files
        os.remove(rt.get_unit_test_log_file())


if __name__ == '__main__':
    unittest.main()
