import os
import sys
import importlib.util
import importlib.machinery
import types
import numpy as np

def apply_patches():
    # 1. Apply numpy patches to prevent representation/issubdtype recursion and TypeErrors
    try:
        import numpy.core._dtype as nd
        _orig_scalar_str = nd._scalar_str
        def patched_scalar_str(dtype, short=False):
            try:
                return _orig_scalar_str(dtype, short=short)
            except Exception:
                try:
                    return getattr(dtype, 'name', 'unknown')
                except Exception:
                    return "unknown"
        nd._scalar_str = patched_scalar_str
    except Exception:
        pass

    _orig_issubdtype = np.issubdtype
    sctypeDict = getattr(np, 'sctypeDict', {})

    def patched_issubdtype(arg1, arg2):
        t1 = arg1
        if hasattr(t1, 'type'):
            t1 = t1.type
        elif isinstance(t1, str) and t1 in sctypeDict:
            t1 = sctypeDict[t1]
            
        t2 = arg2
        if hasattr(t2, 'type'):
            t2 = t2.type
        elif isinstance(t2, str) and t2 in sctypeDict:
            t2 = sctypeDict[t2]
            
        mapping = {
            int: np.integer,
            float: np.floating,
            bool: np.bool_,
            str: np.str_,
            object: np.object_
        }
        t1 = mapping.get(t1, t1)
        t2 = mapping.get(t2, t2)
        
        if isinstance(t1, type) and isinstance(t2, type):
            try:
                return issubclass(t1, t2)
            except Exception:
                pass
                
        return _orig_issubdtype(arg1, arg2)

    np.issubdtype = patched_issubdtype
    import numpy.core.numerictypes as nt
    if hasattr(nt, 'issubdtype'):
        nt.issubdtype = patched_issubdtype

    # 2. Dynamically find scipy interpolate directory and pre-load/patch dfitpack
    try:
        scipy_spec = importlib.util.find_spec("scipy")
        if scipy_spec and scipy_spec.submodule_search_locations:
            scipy_dir = scipy_spec.submodule_search_locations[0]
            interpolate_dir = os.path.join(scipy_dir, "interpolate")
            pyd_path = None
            if os.path.exists(interpolate_dir):
                for f in os.listdir(interpolate_dir):
                    if f.startswith("dfitpack") and f.endswith(".pyd"):
                        pyd_path = os.path.join(interpolate_dir, f)
                        break
            
            if pyd_path:
                # Pre-register scipy and scipy.interpolate dummy modules so we can load the extension
                if "scipy" not in sys.modules:
                    sys.modules["scipy"] = types.ModuleType("scipy")
                if "scipy.interpolate" not in sys.modules:
                    sys.modules["scipy.interpolate"] = types.ModuleType("scipy.interpolate")
                
                # Load the extension pyd directly
                spec = importlib.util.spec_from_file_location("scipy.interpolate.dfitpack", pyd_path)
                dfitpack_module = importlib.util.module_from_spec(spec)
                sys.modules["scipy.interpolate.dfitpack"] = dfitpack_module
                spec.loader.exec_module(dfitpack_module)
                
                # Patch types hierarchy to bypass C-level dfitpack_int registration/evaluation failure
                class MockIntVar:
                    dtype = np.dtype(np.int32)
                class MockTypes:
                    intvar = MockIntVar()
                dfitpack_module.types = MockTypes()
                
                # Clean up the dummy scipy/scipy.interpolate modules from sys.modules
                # (so that subsequent standard imports will load the actual package files normally,
                # but they will reuse the already-patched scipy.interpolate.dfitpack module in sys.modules)
                if "scipy" in sys.modules and not hasattr(sys.modules["scipy"], "__file__"):
                    del sys.modules["scipy"]
                if "scipy.interpolate" in sys.modules and not hasattr(sys.modules["scipy.interpolate"], "__file__"):
                    del sys.modules["scipy.interpolate"]
    except Exception:
        pass

    # 3. Mock 'datasets' module in sys.modules to bypass pyarrow DLL load conflicts
    try:
        dummy_datasets = types.ModuleType("datasets")
        class DummyClass:
            pass
        dummy_datasets.Dataset = DummyClass
        dummy_datasets.DatasetDict = DummyClass
        dummy_datasets.IterableDataset = DummyClass
        dummy_datasets.IterableDatasetDict = DummyClass
        dummy_datasets.Value = DummyClass
        dummy_datasets.__version__ = "3.0.0"
        
        # Set __spec__ so find_spec behaves correctly
        dummy_datasets.__spec__ = importlib.machinery.ModuleSpec(
            name="datasets",
            loader=None,
            origin="mocked"
        )
        sys.modules["datasets"] = dummy_datasets
    except Exception:
        pass

# Apply the patches at module load time
apply_patches()
