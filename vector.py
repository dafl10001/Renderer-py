import math

class vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return vec2(self.x * other, self.y * other)
        return vec2(self.x * other.x, self.y * other.y)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __eq__(self, other):
        if not isinstance(other, vec2):
            return False
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"vec2({self.x}, {self.y})"

    @property
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        length = self.length
        if length == 0:
            return vec2(0, 0)
        self.x /= length
        self.y /= length


class vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return vec3(self.x * other, self.y * other, self.z * other)
        return vec3(self.x * other.x, self.y * other.y, self.z * other.z)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __eq__(self, other):
        if not isinstance(other, vec3):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __repr__(self):
        return f"vec3({self.x}, {self.y}, {self.z})"

    @property
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalize(self):
        length = self.length
        if length == 0:
            return vec3(0, 0, 0)
        self.x /= length
        self.y /= length
        self.z /= length

    def map2(self, k):
        return vec2(self.x / (k - self.z), self.y / (k - self.z))


class vec4:
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __add__(self, other):
        return vec4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)

    def __sub__(self, other):
        return vec4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return vec4(self.x * other, self.y * other, self.z * other, self.w * other)
        return vec4(self.x * other.x, self.y * other.y, self.z * other.z, self.w * other.w)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return vec4(self.x / other, self.y / other, self.z / other, self.w / other)
        return vec4(self.x / other.x, self.y / other.y, self.z / other.z, self.w / other.w)

    def __eq__(self, other):
        if not isinstance(other, vec4):
            return False
        return (self.x == other.x and self.y == other.y and 
                self.z == other.z and self.w == other.w)

    def __repr__(self):
        return f"vec4({self.x}, {self.y}, {self.z}, {self.w})"
    
    def to_tuple(self):
        """Useful for converting to RGB/RGBA for byte writing"""
        return (self.x, self.y, self.z, self.w)
    

    @property
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2)

    def normalize(self):
        length = self.length
        if length == 0:
            return vec4(0, 0, 0)
        self.x /= length
        self.y /= length
        self.z /= length
        self.w /= length
    
    def map3(self, k):
        return vec3(self.x / (k - self.w), self.y / (k - self.w), self.z / (k - self.w))
    
    def map2(self, k3, k2):
        return self.map3(k3).map2(k2)


class transform3:
    def __init__(self, position: vec3, scale: vec3, rotation: vec3):
        self.position = position
        self.scale = scale
        self.rotation = rotation
    
    def mapVertices(self, vertices: list[vec3]):
        sx, cx = math.sin(self.rotation.x), math.cos(self.rotation.x)
        sy, cy = math.sin(self.rotation.y), math.cos(self.rotation.y)
        sz, cz = math.sin(self.rotation.z), math.cos(self.rotation.z)

        transformed_list = []

        for v in vertices:
            x = v.x * self.scale.x
            y = v.y * self.scale.y
            z = v.z * self.scale.z

            new_y = y * cx - z * sx
            new_z = y * sx + z * cx
            y, z = new_y, new_z

            new_x = x * cy + z * sy
            new_z = -x * sy + z * cy
            x, z = new_x, new_z

            new_x = x * cz - y * sz
            new_y = x * sz + y * cz
            x, y = new_x, new_y

            final_v = vec3(x + self.position.x, 
                           y + self.position.y, 
                           z + self.position.z)
            
            transformed_list.append(final_v)

        return transformed_list

