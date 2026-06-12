
import sys # for error messages
import pydantic
import json # for obvious purpose
# from enum import Enum
from typing import Literal
import re # to clean shared list name from category reference - remove //.^


# STDOUT_COLOR_RED = "\033[91m"
STDOUT_COLOR_RED = "\033[31m" # for error messages
STDOUT_COLOR_RESET = "\033[0m"
STDOUT_COLOR_GREEN = "\033[32m"




class ErrFieldNoData(Exception):
    """Internal, should be intercepted"""

class ErrorItemNotIterable(Exception):
    """Raised from list_categories()"""
    pass

def validate_name(name_str,mdmfield):
    name_str_clean = f'{name_str}'.strip()
    return True \
        and isinstance(name_str,str) \
        and (name_str_clean==name_str) \
        and (name_str_clean==mdmfield.Name)
        



def process_field(mdmfield):
    """Receives: mdm field object, returns: a tuple of type constant for pydantic and type constraints for pydantic"""

    def process_fields(mdmfields):
        fields = {}
        for mdmfield in mdmfields:
            try:
                fields[mdmfield.Name] = process_field(mdmfield)
                helper_fields = []
                try:
                    helper_fields = mdmfield.HelperFields
                except:
                    pass
                for mdmhelperfield in helper_fields:
                    try:
                        fields[f'{mdmfield.Name}.{mdmhelperfield.Name}'] = process_field(mdmhelperfield)
                    except ErrFieldNoData:
                        pass
            except ErrFieldNoData:
                pass
        return fields
    
    def list_categories(mdmfield):
        try:
            mdmelements = mdmfield.Elements
        except AttributeError as e:
            raise ErrorItemNotIterable(f'Error: item is not iterable; can\'; get list of categories') from e
        for mdmcat in mdmelements:
            catname = f'{mdmcat}'
            try:
                catname = f'{mdmcat.Name}'
            except:
                pass
            try:
                if mdmcat.IsReference:
                    try:
                        sl_name_clean = re.sub(r'[\^\\/\.]','',mdmcat.ReferenceName,flags=re.I|re.DOTALL)
                        mdmsharedlist = mdmfield.Document.Types[sl_name_clean]
                        yield from list_categories(mdmsharedlist)
                    except Exception as e:
                        raise Exception(f'Was not able to refer to a Shared List "{mdmcat.ReferenceName}": {e}') from e
                elif mdmcat.Type==0:
                    yield mdmcat
                elif (mdmcat.Type==1) or (mdmcat.Type==13):
                    # yield mdmcat
                    yield from list_categories(mdmcat)
                elif (mdmcat.Type==4097) or (re.match(r'^\s*?\d+\s*?$','{s}'.format(s=mdmcat.Name),flags=re.I|re.DOTALL)):
                    yield mdmcat
                else:
                    try:
                        yield from list_categories(mdmcat)
                    except ErrorItemNotIterable:
                        yield mdmcat
            except Exception as e:
                print(f'{STDOUT_COLOR_RED}Failed when processing element or category: {catname}{STDOUT_COLOR_RESET}',file=sys.stderr)
                raise e
    
    def build_properties(mdmfield):
        result = {}
        for index_prop in range( 0, mdmfield.Properties.Count ):
            name = f'{mdmfield.Properties.Name(index_prop)}'
            value = mdmfield.Properties[name]
            result[name] = value
        return result
    
    def make_pydmodel_from_iterations(iterations,pydfieldmodel):
        loop_fields = {}
        for iter in iterations:
            loop_fields[iter] = (pydfieldmodel, ...)
        return pydantic.create_model(
            'Dummy_Loop_Name',
            **loop_fields
        )
    
    name = mdmfield.Name
    field_info_kwargs = {}
    mustanswer = None
    try:
        mustanswer = mdmfield.MustAnswer
    except:
        pass
    if mustanswer is not None and mustanswer == False:
        field_info_kwargs['default'] = None
    field_info_kwargs['title'] = mdmfield.Label
    props = {}
    props.update(build_properties(mdmfield))
    props['MDM:Name'] = mdmfield.Name
    min = None
    try:
        min = mdmfield.Validation.MinValue
    except:
        pass
    if min is not None:
        props['MDM:MinValue'] = min
    max = None
    try:
        max = mdmfield.Validation.MaxValue
    except:
        pass
    if max is not None:
        props['MDM:MaxValue'] = max
    field_info_kwargs['description'] = json.dumps(props)

    try:
        object_type_value = mdmfield.ObjectTypeValue
        # ObjectTypeValue constants:
        # 0 = Question
        # 1 = Array
        # 2 = Grid
        # 3 = Class
        # 4 = Element
        # 10 = VariableInstance
        # 16 = Variables
        # 27 = Root MDM Document
        # 38 = Page
        if object_type_value==0:
            # regular variable
            data_type = mdmfield.DataType
            if data_type==0:
                # info
                raise ErrFieldNoData
            elif data_type==1:
                # long
                py_type = int
                min = None
                try:
                    min = mdmfield.Validation.MinValue
                except:
                    pass
                if min is not None:
                    field_info_kwargs['ge'] = min
                max = None
                try:
                    max = mdmfield.Validation.MaxValue
                except:
                    pass
                if max is not None:
                    field_info_kwargs['le'] = max
                field_info = pydantic.Field(**field_info_kwargs)
                return py_type, field_info
            elif data_type==6:
                # double
                py_type = float
                min = None
                try:
                    min = mdmfield.Validation.MinValue
                except:
                    pass
                if min is not None:
                    field_info_kwargs['ge'] = min
                max = None
                try:
                    max = mdmfield.Validation.MaxValue
                except:
                    pass
                if max is not None:
                    field_info_kwargs['le'] = max
                field_info = pydantic.Field(**field_info_kwargs)
                return py_type, field_info
            elif data_type==7:
                # boolean
                py_type = bool
                field_info = pydantic.Field(**field_info_kwargs)
                return py_type, field_info
            elif data_type==2:
                # text
                py_type = str
                min = None
                try:
                    min = mdmfield.Validation.MinValue
                except:
                    pass
                if min is not None:
                    field_info_kwargs['min_length'] = min
                max = None
                try:
                    max = mdmfield.Validation.MaxValue
                except:
                    pass
                if max is not None:
                    field_info_kwargs['max_length'] = max
                regex = None
                try:
                    regex = mdmfield.Validation
                except:
                    pass
                try:
                    if regex is not None:
                        regex = f'^(?:{regex})$'
                except:
                    pass
                if regex is not None:
                    field_info_kwargs['pattern'] = regex
                field_info = pydantic.Field(**field_info_kwargs)
                return py_type, field_info
            elif data_type==5:
                # date
                py_type = str
                field_info_kwargs['format'] = 'date'
                field_info = pydantic.Field(**field_info_kwargs)
                return py_type, field_info
            elif data_type==3:
                # categorical
                mdmcategories = list_categories(mdmfield)
                values = [mdmcat.Label for mdmcat in mdmcategories]
                py_type = Literal[*values]
                field_info = pydantic.Field(**field_info_kwargs)
                return py_type, field_info
            pass
        elif object_type_value==1:
            # array (loop)
            mdmcategories = list_categories(mdmfield)
            iterations = [mdmcat.Label for mdmcat in mdmcategories]
            fields = {}
            fields.update(process_fields(mdmfield.Fields))
            pydfieldmodel = pydantic.create_model(name,**fields)
            # pydmodel = list[pydfieldmodel]
            pydmodel = make_pydmodel_from_iterations(iterations,pydfieldmodel)
            field_info = pydantic.Field(**field_info_kwargs)
            return (pydmodel,field_info)
        elif object_type_value==2:
            # Grid (it seems it's something different than Array, but I can't understand their logic; maybe it's different because it has a different db setup in case data, I don't know)
            # Execute Error: The '<Object>.IGrid' type does not support the 'categories' property
            mdmcategories = list_categories(mdmfield)
            iterations = [mdmcat.Label for mdmcat in mdmcategories]
            fields = {}
            fields.update(process_fields(mdmfield.Fields))
            pydfieldmodel = pydantic.create_model(name,**fields)
            # pydmodel = list[pydfieldmodel]
            pydmodel = make_pydmodel_from_iterations(iterations,pydfieldmodel)
            field_info = pydantic.Field(**field_info_kwargs)
            return (pydmodel,field_info)
        elif object_type_value==3:
            # class (block) - means "compond" object
            fields = {}
            fields.update(process_fields(mdmfield.Fields))
            pydmodel = pydantic.create_model(name,**fields)
            field_info = pydantic.Field(**field_info_kwargs)
            return pydmodel, field_info
        elif object_type_value==27:
            # root mdm document
            fields = {}
            fields.update(process_fields(mdmfield.Fields))
            fields.update(process_fields(mdmfield.Pages))
            pydmodel = pydantic.create_model('MDM',**fields)
            field_info = pydantic.Field(**field_info_kwargs)
            return pydmodel, field_info
        elif object_type_value==38:
            # page
            fields = {}
            for mdmfield in mdmfield:
                try:
                    fields[mdmfield.Name] = process_field(mdmfield)
                except ErrFieldNoData:
                    pass
            pydmodel = pydantic.create_model(name,**fields)
            field_info = pydantic.Field(**field_info_kwargs)
            return pydmodel, field_info
        # elif object_type_value==16:
        #     # not sure what is it, an example is Respondent.Serial (in some projects)
        #     pass
        # elif object_type_value==10:
        #     # not sure what it is either
        #     pass
        else:
            raise ValueError(f'unrecognized object data type: {object_type_value}')

    except ErrFieldNoData as e:
        raise e
    except Exception as e:
        print(f'{STDOUT_COLOR_RED}Failed when processing field: {name}{STDOUT_COLOR_RESET}',file=sys.stderr)
        raise e
    raise Exception(f'process_field: reached to the end and still did not return anything?')
