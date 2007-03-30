from zope.interface import implements
from zope.component import adapts

from persistent.dict import PersistentDict

from zope.annotation.interfaces import IAnnotations

from AccessControl import getSecurityManager
from webdav.LockItem import LockItem

from plone.locking.interfaces import ILockable
from plone.locking.interfaces import INonStealableLock
from plone.locking.interfaces import ITTWLockable
from plone.locking.interfaces import STEALABLE_LOCK

ANNOTATION_KEY = 'plone.locking'

class TTWLockable(object):
    """An object that is being locked through-the-web
    """

    implements(ILockable)
    adapts(ITTWLockable)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)
        self.locks = annotations.setdefault(ANNOTATION_KEY, PersistentDict())

    def lock(self, lock_type=STEALABLE_LOCK, children=False):
        if not self.locked():
            user = getSecurityManager().getUser()
            depth = children and 'infinity' or 0
            lock = LockItem(user, depth=depth)
            token = lock.getLockToken()
            self.context.wl_setLock(token, lock)

            self.locks[lock_type.__name__] = dict(type = lock_type,
                                                  token = token)

    def unlock(self, lock_type=STEALABLE_LOCK, stealable_only=True):
        if not self.locked():
            return

        if not lock_type.stealable or not stealable_only \
           or self.stealable(lock_type):
            key = self.locks.get(lock_type.__name__, None)
            if key:
                self.context.wl_delLock(key['token'])
                del self.locks[lock_type.__name__]

    def clear_locks(self):
        self.context.wl_clearLocks()
        self.locks.clear()

    def locked(self):
        return bool(self.context.wl_isLocked())

    def can_safely_unlock(self, lock_type=STEALABLE_LOCK):
        if not lock_type.user_unlockable:
            return False

        info = self.lock_info()
        # There is no lock, so return True
        if len(info) == 0:
            return True

        userid = getSecurityManager().getUser().getId()
        for l in info:
            # There is another lock of a different type
            if l['type'].__name__ != lock_type.__name__:
                return False
            # The lock is in fact held by the current user
            if l['creator'] == userid:
                return True
        return False

    def stealable(self, lock_type=STEALABLE_LOCK):
        # If the lock type is not stealable ever, return False
        if not lock_type.stealable:
            return False
        # Can't steal locks of a different type
        for l in self.lock_info():
            if l['type'].__name__ != lock_type.__name__:
                return False
        # The lock type is stealable, and the object is not marked as 
        # non-stelaable, so return True
        if not INonStealableLock.providedBy(self.context):
            return True
        # Lock type is stealable, object is not stealable, but return True
        # anyway if we can safely unlock this object (e.g. we are the owner)
        return self.can_safely_unlock(lock_type)

    def lock_info(self):
        info = []
        rtokens = dict([(v['token'], v['type']) for v in self.locks.values()])
        for lock in self.context.wl_lockValues(1):
            if not lock.isValid():
                continue # Skip invalid/expired locks
            token = lock.getLockToken()
            info.append({
                'creator' : lock.getCreator()[1],
                'time'    : lock.getModifiedTime(),
                'token'   : token,
                'type'    : rtokens.get(token, None),
            })
        return info
