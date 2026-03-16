import pytest
@pytest.mark.regression
def test_demo():
    print("This is a test demo")
    assert 1 ==1

@pytest.mark.regression
def test_demo2():
    print("This is a test demo2")



@pytest.mark.regression
@pytest.mark.smoke
def test_demo3():
    print("This is a test demo3")


@pytest.mark.skip
@pytest.mark.regression
def test_demo4():
    print("This is a test demo4")
