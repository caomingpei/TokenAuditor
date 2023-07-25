from oracle.authority_management import *
from oracle.freezing_backdoor import *
from oracle.preallocation import *
from oracle.token_compatibility import *

ALL_ORACLE = [PreAllocation, TokenCompatibility, AuthorityManagement, FreezingBackdoor]
# ALL_ORACLE = [PreAllocation, AuthorityManagement, FreezingBackdoor]
# ALL_ORACLE = [FreezingBackdoor, AuthorityManagement]
# ALL_ORACLE = [PreAllocation]
