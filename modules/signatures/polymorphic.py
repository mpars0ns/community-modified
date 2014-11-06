# Copyright (C) 2013-2014 Lord Alfred Remorin, Accuvant Inc. (bspengler@accuvant.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from math import fabs

from lib.cuckoo.common.abstracts import Signature

try:
    import pydeep
    HAVE_SSDEEP = True
except ImportError:
    HAVE_SSDEEP = False

class Polymorphic(Signature):
    name = "polymorphic"
    description = "Creates a file similar to target file"
    severity = 3
    categories = ["persistence"]
    authors = ["lordr", "Accuvant"]
    minimum = "1.2"

    def run(self):
        found_polymorphic = False
        if self.results["target"]["category"] == "file":
            target_ssdeep = self.results["target"]["file"]["ssdeep"]
            target_sha1 = self.results["target"]["file"]["sha1"]
            target_size = self.results["target"]["file"]["size"]

            if target_ssdeep == "" or target_ssdeep == None:
                return False

            for drop in self.results["dropped"]:
                if drop["sha1"] == target_sha1:
                    continue
                if fabs(target_size - drop["size"]) >= 1024:
                    continue
                drop_ssdeep = drop["ssdeep"]
                if drop_ssdeep == "" or drop_ssdeep == None:
                    continue
                try:
                    percent = pydeep.compare(target_ssdeep, drop_ssdeep)
                    if percent > 20:
                        found_polymorphic = True
                        for path in drop["guest_paths"]:
                            self.data.append({"file" : path})
                        self.data.append({"percent_match" : percent})
                except:
                    continue

        return found_polymorphic
