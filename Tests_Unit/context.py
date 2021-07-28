def get():
    """Adds the curret folder to the system path. Used to facilitate module import.
    
    ::

        import os
        os.chdir("directory/containing/my/module")
        import context
        context.get()
        import myModule
    """
    import sys, os
    sys.path.append(
        os.path.abspath(
            "."
        )
    )