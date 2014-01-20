import ldapom


class InvalidDefinition(Exception):
    pass


class Field(object):

    _encoder = None
    _decoder = None

    def __init__(self, name, default=None, primary=False, singlevalue=None, nullable=False, null_if_blank=True):
        self.default = default
        self.name = name
        self.primary = primary
        self.singlevalue = singlevalue
        self.nullable = nullable
        self.null_if_blank = null_if_blank

    def _get_value(self, obj):
        key = '_field_{0}_value'.format(self.name)
        value = getattr(obj, key, self.default)
        if self._decoder:
            value = self._decoder(obj, value)
        return value

    def _set_value(self, obj, value):
        key = '_field_{0}_value'.format(self.name)
        if self._encoder:
            value = self._encoder(obj, value)
        setattr(obj, key, value)

    def __set__(self, obj, value):
        self._set_value(obj, value)

    def __get__(self, obj, obj_type):
        return self._get_value(obj)

    def encoder(self, func):
        self._encoder = func

    def decoder(self, func):
        self._decoder = func


class SingleValueField(Field):
    ""
    def __get__(self, obj, obj_type):
        value = self._get_value(obj)
        if isinstance(value, set) and len(value) == 1:
            return list(value)[0]
        if isinstance(value, set) and len(value) > 1:
            raise ValueError("Single value field {0}.{1} has multiple values: {2}".format(
                obj.__class__.__name__,
                self.name,
                value,
            ))
        return value


class _Meta(type):

    def __init__(cls, name, bases, attrs):
        primary_fields = []
        cls._fields = {}
        cls._raw_fields = {}
        if '__NO_ORM_METACLASS__' in attrs:
            return

        for field_name, field in attrs.items():
            if not isinstance(field, Field):
                continue

            cls._fields[field_name] = field
            cls._raw_fields[field.name] = field_name

            if field.primary:
                primary_fields.append(field_name)

        if len(primary_fields) > 1:
            raise InvalidDefinition(
                'Model {1}.{0} has more than one primary attribute'.format(name, cls.__module__)
            )
        if len(primary_fields) == 0:
            raise InvalidDefinition(
                'Model {1}.{0} does not have any primary attribute'.format(name, cls.__module__)
            )
        cls._primary_field = primary_fields[0]
        # return super(_Meta, cls).__init__(name, bases, attrs)


class Base(object):

    _connection = None

    base_dn = None
    all_search_filter = None
    object_classes = ['top']

    __metaclass__ = _Meta
    __NO_ORM_METACLASS__ = True

    # Setted by metaclass
    _fields = {}
    _primary_field = None

    def __init__(self, **kwargs):
        for field_name, field in self._fields.items():
            if field_name in kwargs:
                setattr(self, field_name, kwargs.pop(field_name))
                # field.value = kwargs.pop(field_name)

        if kwargs:
            raise TypeError('Invalid kwargs passed: {0}'.format(', '.join(kwargs.keys())))

    def get_pkey_value(self):
        return getattr(self, self._primary_field)

    @classmethod
    def from_entry(cls, entry):
        obj = cls()
        entry.fetch()
        for attr in entry._attributes:
            key = cls._raw_fields.get(attr.name)
            if not key:
                continue
            value = getattr(entry, attr.name)
            setattr(obj, key, value)
        return obj

    def refresh(self):
        entry = self._connection.get_entry(self.get_dn())
        entry.fetch()
        for attr in entry._attributes:
            key = self._raw_fields.get(attr.name)
            if not key:
                continue
            value = getattr(entry, attr.name)
            setattr(self, key, value)

    @classmethod
    def all(cls):
        for entry in cls._connection.search(search_filter=cls.all_search_filter, base=cls.base_dn):
            yield cls.from_entry(entry)

    @classmethod
    def get(cls, entry_id):
        if entry_id.endswith(cls.base_dn):
            dn = entry_id
        else:
            dn = "{0}={1},{2}".format(
                cls._fields[cls._primary_field].name,
                entry_id,
                cls.base_dn,
            )

        entry = cls._connection.get_entry(dn)
        if not entry.exists():
            return

        return cls.from_entry(entry)

    def get_dn(self, pkey_value=None):
        pkey_raw_name = self._fields[self._primary_field].name
        pkey_value = getattr(self, self._primary_field)
        return "{0}={1},{2}".format(
            pkey_raw_name,
            pkey_value,
            self.base_dn
        )

    def pre_save(self, entry):
        pass

    def save(self):
        if not getattr(self, self._primary_field, None):
            raise ValueError('Primary field {0} not set'.format(self._primary_field))

        entry = ldapom.LDAPEntry(self._connection, self.get_dn())

        for field_name, field in self._fields.items():
            value = getattr(self, field_name)
            if not field.nullable and value is None:
                raise ValueError('Field {0}.{1} must not be None'.format(self.__class__.__name__, field_name))
            if field.null_if_blank and not value:
                value = None
            if value is None:
                delattr(entry, field.name)
            else:
                setattr(entry, field.name, value)
        entry.objectClass = self.object_classes
        self.pre_save(entry)
        entry.save()

    def rename(self, newname):
        raise NotImplementedError()

    def remove(self):
        if not getattr(self, self._primary_field, None):
            raise ValueError('Primary field {0} not set'.format(self._primary_field))
        entry = ldapom.LDAPEntry(self._connection, self.get_dn())
        entry.delete()

    def exists(self):
        entry = ldapom.LDAPEntry(self._connection, self.get_dn())
        return entry.exists()
