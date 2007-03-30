from zope.component import getUtility

from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFCore.interfaces import IURLTool

from DateTime import DateTime
from datetime import timedelta

from plone.locking.interfaces import ILockable

class LockingOperations(BrowserView):
    """Lock acquisition and stealing operations
    """

    def force_unlock(self, redirect=True):
        """Steal the lock.

        If redirect is True, redirect back to the context URL, i.e. reload
        the page.
        """
        lockable = ILockable(self.context)
        lockable.unlock()
        if redirect:
            self.request.RESPONSE.redirect(self.context.absolute_url())

    def safe_unlock(self):
        """Unlock the object if the current user has the lock
        """
        info = ILockable(self.context)
        if info.can_safely_unlock():
            lockable = ILockable(self.context)
            lockable.unlock()

class LockingInformation(BrowserView):
    """Lock information
    """

    def is_locked(self):
        lockable = ILockable(aq_inner(self.context))
        return lockable.locked()

    def is_locked_for_current_user(self):
        """True if this object is locked for the current user (i.e. the
        current user is not the lock owner)
        """
        lockable = ILockable(aq_inner(self.context))
        # Faster version - we rely on the fact that can_safely_unlock() is
        # True even if the object is not locked
        return not lockable.can_safely_unlock()
        # return lockable.locked() and not lockable.can_safely_unlock()

    def lock_is_stealable(self):
        """Find out if the lock is stealable
        """
        lockable = ILockable(self.context)
        return lockable.stealable()

    def lock_info(self):
        """Get information about the current lock, a dict containing:

        creator - the id of the user who created the lock
        fullname - the full name of the lock creator
        author_page - a link to the home page of the author
        time - the creation time of the lock
        time_difference - a string representing the time since the lock was
        acquired.
        """

        portal_membership = getUtility(IMembershipTool)
        portal_url = getUtility(IURLTool)
        lockable = ILockable(aq_inner(self.context))
        url = portal_url()
        for info in lockable.lock_info():
            creator = info['creator']
            time = info['time']
            token = info['token']
            lock_type = info['type']
            author_page = "%s/author/%s" % (url, creator)
            member = portal_membership.getMemberById(creator)
            if member:
                fullname = member.getProperty('fullname', None) or creator

            time_difference = self._getNiceTimeDifference(time)

            return {
                'creator'         : creator,
                'fullname'        : fullname,
                'author_page'     : author_page,
                'time'            : time,
                'time_difference' : time_difference,
                'token'           : token,
                'type'            : lock_type,
            }

    def _getNiceTimeDifference(self, baseTime):
        now = DateTime()
        days = int(round(now - DateTime(baseTime)))
        delta = timedelta(now - DateTime(baseTime))
        days = delta.days
        hours = int(delta.seconds / 3600)
        minutes = (delta.seconds - (hours * 3600)) /60

        dateString = ""
        if days == 0:
            if hours == 0:
                if delta.seconds < 120:
                    dateString = "1 minute"
                else:
                    dateString = "%s minutes" % minutes
            elif hours == 1:
                dateString = "%s hour and %s minutes" % (hours, minutes)
            else:
                dateString = "%s hours and %s minutes" % (hours, minutes)
        else:
            if days == 1:
                dateString = "%s day and %s hours" % (days, hours)
            else:
                dateString = "%s days and %s hours" % (days, hours)
        return dateString
